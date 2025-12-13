# CouchController Architecture

Technical overview of CouchController's design and implementation.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                            │
│  ┌────────────┐      ┌──────────────┐      ┌─────────────────┐ │
│  │   Game     │◄─────┤   Virtual    │◄─────┤   Network       │ │
│  │  Running   │      │  Controllers │      │   Server        │ │
│  └────────────┘      └──────────────┘      └────────┬────────┘ │
│        │                                              │         │
│        │                                              │         │
│  ┌─────▼──────┐                                      │         │
│  │  Screen    │                                      │         │
│  │  Capture   ├──────────────────────────────────────┘         │
│  └────────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                      Network (UDP)
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      CLIENT MACHINE(S)                          │
│  ┌────────────┐      ┌──────────────┐      ┌─────────────────┐ │
│  │ Controller │─────►│   Input      │─────►│   Network       │ │
│  │  Device    │      │   Capture    │      │   Client        │ │
│  └────────────┘      └──────────────┘      └────────┬────────┘ │
│                                                      │         │
│                                              ┌───────▼────────┐ │
│                                              │  Video Decoder │ │
│                                              │  & Display     │ │
│                                              └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Host Components

#### 1. Screen Capture (`screen_capture.py`)
- **Technology:** MSS (DirectX on Windows)
- **Purpose:** Captures screen at target FPS
- **Optimization:** Threaded capture, minimal overhead
- **Output:** Raw BGR frames

#### 2. Video Encoder (`screen_capture.py`)
- **Technology:** PyAV (FFmpeg) with H.264
- **Codec Settings:**
  - Preset: `ultrafast`
  - Tune: `zerolatency`
  - RC Mode: Constant Bitrate (CBR)
  - No lookahead (rc-lookahead=0)
- **Purpose:** Encode frames for network transmission
- **Output:** H.264 encoded packets

#### 3. Virtual Controller Manager (`virtual_controller.py`)
- **Technology:** vgamepad + ViGEmBus
- **Purpose:** Create Xbox 360 controllers visible to games
- **Capabilities:**
  - Up to 4 simultaneous controllers
  - Full Xbox 360 button/axis mapping
  - Real-time state updates
- **Latency:** <1ms (direct driver injection)

#### 4. Network Server (`network/server.py`)
- **Protocol:** UDP (low latency)
- **Ports:**
  - 7777: Control (TCP-like handshake over UDP)
  - 7778: Video stream (broadcast)
  - 7779: Controller input (unicast)
- **Threading:** Separate threads for input/video
- **Features:**
  - Client connection management
  - Timeout detection
  - Controller slot assignment

### Client Components

#### 1. Controller Input (`controller_input.py`)
- **Technology:** pygame
- **Purpose:** Read controller state
- **Polling Rate:** 120 Hz (8.3ms intervals)
- **Mapping:** Maps any controller to Xbox 360 layout
- **Features:**
  - Deadzone filtering
  - Multi-controller support
  - Trigger normalization

#### 2. Network Client (`network/client.py`)
- **Protocol:** UDP
- **Purpose:** Send input, receive video
- **Threading:** Separate video receiver thread
- **Features:**
  - Auto-reconnect
  - Keepalive pings
  - Sequence tracking

#### 3. Video Decoder (`client.py`)
- **Technology:** PyAV (FFmpeg)
- **Codec:** H.264
- **Purpose:** Decode received frames
- **Output:** RGB frames

#### 4. Display (`client.py`)
- **Technology:** pygame
- **Purpose:** Show host's screen
- **Features:**
  - Auto-scaling
  - Fullscreen support
  - Resizable window

## Network Protocol

### Message Format

All messages use a common header:

```
┌──────────┬───────────┬──────────┬───────────┐
│   Type   │ Sequence  │  Length  │  Payload  │
│  (1 byte)│ (3 bytes) │(4 bytes) │ (N bytes) │
└──────────┴───────────┴──────────┴───────────┘
```

### Message Types

| Type | Name | Direction | Purpose |
|------|------|-----------|---------|
| 0 | HELLO | Client → Host | Initial connection |
| 1 | WELCOME | Host → Client | Connection accepted |
| 2 | PING | Bidirectional | Keepalive |
| 3 | PONG | Bidirectional | Keepalive response |
| 4 | DISCONNECT | Bidirectional | Clean disconnect |
| 10 | CONTROLLER_STATE | Client → Host | Controller input |
| 11 | CONTROLLER_ASSIGN | Host → Client | Slot assignment |
| 20 | VIDEO_FRAME | Host → Client | Encoded frame |
| 21 | VIDEO_CONFIG | Host → Client | Stream config |

### Controller State Format

14 bytes total:
```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Buttons  │ LStick X │ LStick Y │ RStick X │ RStick Y │ Trigger L│ Trigger R│
│ (2 bytes)│(2 bytes) │(2 bytes) │(2 bytes) │(2 bytes) │ (1 byte) │ (1 byte) │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

Buttons packed as bits:
```
Bit:  15-14 13     12     11      10    9      8      7      6     5     4    3    2    1    0
      Res  DRight DLeft  DDown   DUp   RStick LStick Start  Back  RB    LB   Y    X    B    A
```

## Performance Characteristics

### Latency Breakdown

For 60 FPS streaming on LAN:

| Component | Latency | Notes |
|-----------|---------|-------|
| Screen capture | ~1-2ms | DirectX capture |
| Video encoding | ~5-10ms | H.264 ultrafast |
| Network transmission | ~1-5ms | LAN, UDP |
| Video decoding | ~5-10ms | H.264 decode |
| Display | ~16ms | 60Hz vsync |
| Controller polling | ~8ms | 120Hz polling |
| Controller network send | ~1ms | UDP |
| Virtual controller inject | <1ms | Driver level |
| **Total (input to action)** | **~20-30ms** | Screen lag higher |

### Bandwidth Usage

At 1920x1080, 60 FPS, 5 Mbps:
- Video stream: ~5 Mbps per client
- Controller input: ~14 KB/s per client (negligible)
- 4 clients: ~20 Mbps total

At 1280x720, 30 FPS, 3 Mbps:
- Video stream: ~3 Mbps per client
- 4 clients: ~12 Mbps total

## Design Decisions

### Why UDP?

**Pros:**
- Lower latency than TCP
- No retransmission delays
- Multicast-ready (future feature)

**Cons:**
- Packet loss possible
- No guaranteed delivery

**Mitigation:**
- LAN has minimal packet loss (<0.1%)
- Missing video frames acceptable (next frame arrives soon)
- Critical messages (HELLO/WELCOME) use application-level retry

### Why H.264?

**Pros:**
- Hardware acceleration widely available
- Good compression ratio
- Low-latency modes available
- Universal decoder support

**Alternatives considered:**
- **VP8/VP9:** Similar performance, less hardware support
- **Raw/MJPEG:** Too much bandwidth
- **H.265:** Better compression, higher encode latency

### Why ViGEmBus?

**Pros:**
- Industry standard for virtual controllers
- Excellent game compatibility
- Active maintenance
- Well-documented

**Alternatives considered:**
- **vJoy:** Older, less compatible
- **DirectInput emulation:** Lacks Xbox controller features
- **Custom kernel driver:** Too complex

## Threading Model

### Host

```
Main Thread
├── Component initialization
└── Stats/monitoring

Screen Capture Thread
├── Capture frames at target FPS
└── Queue for encoding

Encoding Thread (implicit in PyAV)
├── Encode frames
└── Callback with encoded data

Network Input Thread
├── Receive controller data
├── Update virtual controllers
└── Handle connections

Network Video Thread (implicit)
└── Broadcast frames to clients
```

### Client

```
Main Thread
├── Component initialization
└── Pygame event loop + display

Controller Thread
├── Poll at 120 Hz
└── Send to network

Video Receiver Thread
├── Receive frames
├── Decode
└── Update display surface

Keepalive Thread
└── Send pings every 2s
```

## Future Improvements

### Planned Features
1. **Audio streaming:** Add microphone/game audio
2. **Auto-discovery:** mDNS/Bonjour for automatic host finding
3. **Adaptive bitrate:** Adjust quality based on network conditions
4. **P2P mode:** Direct client-to-client for co-hosting
5. **Hardware encoding:** Utilize NVENC/QuickSync for lower CPU usage
6. **Multiple monitors:** Select which monitor to stream
7. **Region capture:** Stream only part of screen (game window)

### Optimizations
1. **Zero-copy paths:** Reduce memory copies in video pipeline
2. **GPU upload:** Upload frames to GPU for pygame rendering
3. **Frame interpolation:** Smooth low FPS on client side
4. **Delta encoding:** Send only changed regions
5. **Multicast:** Single stream for multiple clients (LAN only)

## Security Considerations

### Current State
- **No authentication:** Any client can connect
- **No encryption:** Data sent in plaintext
- **No validation:** Minimal input sanitization

### Recommendations for Production
1. Add pre-shared key authentication
2. Implement TLS/DTLS for encryption
3. Rate limiting for DoS protection
4. Input validation and sanitization
5. Network isolation (VLAN/VPN)

**Note:** For LAN use among trusted players, current security is acceptable.

## Platform Support

### Current
- **Windows 10/11:** Full support (host and client)

### Potential
- **Linux:**
  - Client: Already supported (pygame, av)
  - Host: Need uinput for virtual controllers
- **macOS:**
  - Client: Mostly compatible
  - Host: Need driver for virtual controllers
- **Steam Deck:**
  - Client: Should work (Linux-based)
  - Host: Possible with uinput

## Dependencies

### Core Libraries
- **mss:** Cross-platform screen capture
- **av (PyAV):** FFmpeg Python bindings
- **vgamepad:** ViGEmBus Python wrapper
- **pygame:** Controller input and display
- **numpy:** Array operations

### System Dependencies
- **ViGEmBus:** Windows virtual controller driver (host only)
- **FFmpeg:** Video codec libraries (bundled with PyAV)

## Comparison with Alternatives

| Feature | CouchController | Parsec | Steam Remote Play | Moonlight |
|---------|-----------------|--------|-------------------|-----------|
| Self-hosted | ✅ | ❌ | ⚠️ | ✅ |
| LAN-first | ✅ | ❌ | ⚠️ | ✅ |
| Open source | ✅ | ❌ | ❌ | ✅ |
| Low latency | ✅ | ✅ | ⚠️ | ✅ |
| Easy setup | ⚠️ | ✅ | ✅ | ⚠️ |
| Game agnostic | ✅ | ✅ | ❌ | ❌ |

**Key Differentiator:** Complete control over infrastructure and privacy.
