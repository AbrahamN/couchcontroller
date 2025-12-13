"""Screen capture and video encoding for host"""

import time
import threading
from typing import Optional, Callable
import mss
import numpy as np
import av
from queue import Queue, Full


class ScreenCapture:
    """Fast screen capture using mss (DirectX on Windows)"""

    def __init__(self, monitor: int = 1, target_fps: int = 60):
        """
        Initialize screen capture

        Args:
            monitor: Monitor number to capture (1 = primary, 0 = all monitors)
            target_fps: Target frames per second for capture
        """
        self.monitor = monitor
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self._capture_thread = None
        self._sct = None  # Will be created in capture thread

    def get_monitor_info(self):
        """Get information about the selected monitor"""
        # Create temporary sct instance to get monitor info
        with mss.mss() as sct:
            return sct.monitors[self.monitor]

    def capture_frame(self, sct) -> np.ndarray:
        """
        Capture a single frame from the screen

        Args:
            sct: mss instance to use for capture

        Returns:
            numpy array in BGR format (compatible with OpenCV)
        """
        monitor = sct.monitors[self.monitor]
        screenshot = sct.grab(monitor)

        # Convert to numpy array (BGRA -> BGR for encoding)
        frame = np.array(screenshot)[:, :, :3]  # Drop alpha channel
        return frame

    def start_capture(self, callback: Callable[[np.ndarray, float], None]):
        """
        Start continuous screen capture in a separate thread

        Args:
            callback: Function called with (frame, timestamp) for each captured frame
        """
        if self.running:
            return

        self.running = True
        self._capture_thread = threading.Thread(target=self._capture_loop, args=(callback,))
        self._capture_thread.daemon = True
        self._capture_thread.start()

    def _capture_loop(self, callback: Callable[[np.ndarray, float], None]):
        """Continuous capture loop"""
        # Create mss instance in this thread (thread-safe)
        with mss.mss() as sct:
            self._sct = sct
            last_capture = time.perf_counter()

            while self.running:
                start = time.perf_counter()

                try:
                    # Capture frame
                    frame = self.capture_frame(sct)
                    timestamp = time.time()

                    # Call callback with frame
                    callback(frame, timestamp)
                except Exception as e:
                    # Log error but continue capturing
                    import logging
                    logging.error(f"Frame capture error: {e}")
                    time.sleep(0.1)
                    continue

                # Maintain target FPS
                elapsed = time.perf_counter() - start
                sleep_time = max(0, self.frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Track actual FPS
                now = time.perf_counter()
                actual_fps = 1.0 / (now - last_capture) if (now - last_capture) > 0 else 0
                last_capture = now

            self._sct = None

    def stop_capture(self):
        """Stop screen capture"""
        self.running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None

    def __del__(self):
        """Cleanup"""
        self.stop_capture()


class VideoEncoder:
    """
    Hardware-accelerated video encoder using FFmpeg/PyAV
    Optimized for low latency streaming
    """

    def __init__(
        self,
        width: int,
        height: int,
        fps: int = 60,
        bitrate: int = 5_000_000,  # 5 Mbps default
        codec: str = 'h264',
        preset: str = 'ultrafast',
        tune: str = 'zerolatency'
    ):
        """
        Initialize video encoder

        Args:
            width: Frame width
            height: Frame height
            fps: Frames per second
            bitrate: Target bitrate in bits per second
            codec: Video codec (h264, h264_nvenc for NVIDIA GPU)
            preset: Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium)
            tune: Tuning (zerolatency for minimal latency)
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate = bitrate
        self.codec = codec
        self.preset = preset
        self.tune = tune

        # Create in-memory output container
        self.output = av.open('pipe:', mode='w', format='h264')
        self.stream = self.output.add_stream(codec, rate=fps)
        self.stream.width = width
        self.stream.height = height
        self.stream.pix_fmt = 'yuv420p'
        self.stream.bit_rate = bitrate

        # Low latency options
        self.stream.options = {
            'preset': preset,
            'tune': tune,
            'rc-lookahead': '0',  # No lookahead for minimal latency
            'rc': 'cbr',  # Constant bitrate for predictable bandwidth
        }

        self.frame_count = 0

    def encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """
        Encode a frame to H264

        Args:
            frame: BGR numpy array

        Returns:
            Encoded frame bytes, or None if no packet produced yet
        """
        # Convert BGR to RGB
        rgb_frame = frame[:, :, ::-1]

        # Create AVFrame
        av_frame = av.VideoFrame.from_ndarray(rgb_frame, format='rgb24')
        av_frame.pts = self.frame_count
        self.frame_count += 1

        # Encode
        packets = self.stream.encode(av_frame)

        # Return encoded data
        if packets:
            # Concatenate all packet data
            return b''.join(bytes(packet) for packet in packets)
        return None

    def flush(self) -> bytes:
        """Flush encoder and get remaining packets"""
        packets = self.stream.encode(None)
        if packets:
            return b''.join(bytes(packet) for packet in packets)
        return b''

    def close(self):
        """Close encoder"""
        try:
            self.flush()
            self.output.close()
        except:
            pass


class ScreenStreamer:
    """
    High-level screen streaming manager
    Combines screen capture and encoding
    """

    def __init__(
        self,
        monitor: int = 1,
        fps: int = 60,
        bitrate: int = 5_000_000,
        max_queue_size: int = 5
    ):
        """
        Initialize screen streamer

        Args:
            monitor: Monitor to capture
            fps: Target FPS
            bitrate: Target bitrate
            max_queue_size: Max frames to queue before dropping
        """
        self.capture = ScreenCapture(monitor=monitor, target_fps=fps)
        self.encoded_queue = Queue(maxsize=max_queue_size)
        self.encoder = None
        self.running = False

    def start(self, frame_callback: Optional[Callable[[bytes, float], None]] = None):
        """
        Start streaming

        Args:
            frame_callback: Optional callback for encoded frames (data, timestamp)
        """
        # Get monitor dimensions
        monitor_info = self.capture.get_monitor_info()
        width = monitor_info['width']
        height = monitor_info['height']

        # Initialize encoder
        self.encoder = VideoEncoder(
            width=width,
            height=height,
            fps=self.capture.target_fps,
            bitrate=5_000_000
        )

        self.running = True
        self.frame_callback = frame_callback

        # Start capture with encoding callback
        self.capture.start_capture(self._on_frame_captured)

    def _on_frame_captured(self, frame: np.ndarray, timestamp: float):
        """Handle captured frame"""
        if not self.running or not self.encoder:
            return

        # Encode frame
        encoded = self.encoder.encode_frame(frame)

        if encoded:
            # Queue encoded frame
            try:
                self.encoded_queue.put_nowait((encoded, timestamp))
            except Full:
                # Drop frame if queue is full
                pass

            # Call callback if provided
            if self.frame_callback:
                self.frame_callback(encoded, timestamp)

    def get_encoded_frame(self, timeout: float = 0.1) -> Optional[tuple]:
        """
        Get next encoded frame from queue

        Returns:
            (encoded_data, timestamp) or None if timeout
        """
        try:
            return self.encoded_queue.get(timeout=timeout)
        except:
            return None

    def stop(self):
        """Stop streaming"""
        self.running = False
        self.capture.stop_capture()
        if self.encoder:
            self.encoder.close()
            self.encoder = None

    def __del__(self):
        """Cleanup"""
        self.stop()
