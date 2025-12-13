# CouchController Setup Guide

Complete setup instructions for getting CouchController running on Windows.

## Prerequisites

- **Windows 10/11** (both host and clients)
- **Python 3.8 or newer**
- **Xbox/PlayStation/Generic game controller** (for clients)
- **Local network** (LAN or WiFi)

## Installation Steps

### 1. Install Python Dependencies

On both host and client machines:

```bash
# Navigate to the project directory
cd couchcontroller

# Install required packages
pip install -r requirements.txt
```

### 2. Install ViGEmBus Driver (HOST ONLY)

The host machine needs the ViGEmBus driver to create virtual controllers.

1. Download the latest release from: https://github.com/ViGEm/ViGEmBus/releases
2. Download `ViGEmBus_Setup_x64.exe` (or x86 for 32-bit)
3. Run the installer as Administrator
4. Restart your computer

To verify installation:
```bash
# This should work without errors
python -c "import vgamepad; print('ViGEmBus OK')"
```

### 3. Configure Windows Firewall

CouchController needs to communicate over the network.

#### Host Machine:

Create firewall rules for incoming connections:

```powershell
# Run PowerShell as Administrator, then:

# Allow Python through firewall
New-NetFirewallRule -DisplayName "CouchController Host" -Direction Inbound -Program "C:\Path\To\python.exe" -Action Allow

# Or open specific ports (7777-7779)
New-NetFirewallRule -DisplayName "CouchController Ports" -Direction Inbound -Protocol UDP -LocalPort 7777-7779 -Action Allow
```

Alternatively, use Windows Defender Firewall GUI:
1. Open "Windows Defender Firewall with Advanced Security"
2. Click "Inbound Rules" → "New Rule"
3. Select "Program" → Browse to your Python executable
4. Allow the connection
5. Apply to all profiles

#### Client Machine:

Usually no firewall changes needed (outbound connections are allowed by default).

## Usage

### Starting the Host

On the machine running the game:

```bash
# Start with default settings (primary monitor, 60 FPS)
python host.py

# Customize settings
python host.py --monitor 1 --fps 60 --max-clients 4

# See all options
python host.py --help
```

The host will display:
- Its local IP address
- Number of available controller slots
- Connection instructions for clients

**Important:** Start the host BEFORE launching your game, so the virtual controllers are already created.

### Starting the Client

On remote player machines:

```bash
# Connect to host (replace with actual host IP)
python client.py --host 192.168.1.100

# Use a specific controller (if you have multiple)
python client.py --host 192.168.1.100 --controller 1

# Start in fullscreen mode
python client.py --host 192.168.1.100 --fullscreen

# See all options
python client.py --help
```

### Typical Workflow

1. **Host starts CouchController**
   ```bash
   python host.py
   ```

2. **Host notes the IP address** (e.g., `192.168.1.100`)

3. **Host launches the game**
   - The game should detect virtual controllers
   - Configure game for local multiplayer

4. **Clients connect**
   ```bash
   python client.py --host 192.168.1.100
   ```

5. **Clients see host's screen** and can control their assigned player

6. **Play!**

## Network Requirements

### LAN (Recommended)
- All machines on the same local network
- Typical latency: 1-5ms
- Best experience for fast-paced games

### WiFi
- Works but may have higher latency
- Use 5GHz WiFi for better performance
- Host should be wired (Ethernet) if possible

### Internet (Advanced)
- Requires port forwarding on host's router
- Higher latency (depends on connection)
- Not recommended for latency-sensitive games

## Troubleshooting

### Host Issues

**"vgamepad not installed"**
```bash
pip install vgamepad
```

**"ViGEmBus driver not found"**
- Install ViGEmBus driver (see step 2)
- Restart computer after installation

**"No clients can connect"**
- Check firewall settings
- Verify host and clients are on same network
- Try disabling Windows Firewall temporarily to test

**"Screen capture is slow"**
- Lower FPS: `python host.py --fps 30`
- Close other applications
- Check CPU usage

### Client Issues

**"No controller found"**
- Connect controller before starting client
- Check controller in Windows "Game Controllers" settings
- Try a different USB port

**"Connection timeout"**
- Verify host IP address
- Check firewall on host
- Ensure host is running
- Ping the host: `ping 192.168.1.100`

**"Video is laggy"**
- Use wired Ethernet instead of WiFi
- Lower host FPS
- Reduce network traffic on LAN
- Check for WiFi interference

**"Controller input is delayed"**
- Expected latency: 20-50ms on LAN
- Check network latency: `ping -t 192.168.1.100`
- Close bandwidth-heavy applications
- Use wired connection

### General Tips

1. **Use Wired Connections**
   - Host should be wired (Ethernet)
   - Clients can use WiFi (5GHz preferred)

2. **Close Background Apps**
   - Discord, OBS, browsers can impact performance
   - Check Task Manager for CPU/network usage

3. **Monitor Network Performance**
   - Use `ping` to check latency
   - Low latency = better experience

4. **Test Without Game First**
   - Run host and client without a game
   - Verify video streaming works
   - Then launch the game

## Performance Tuning

### For Best Latency (competitive games)
```bash
# Host: Lower FPS, faster encoding
python host.py --fps 30

# Less data to transfer = lower latency
```

### For Best Quality (story/casual games)
```bash
# Host: Higher FPS and bitrate
python host.py --fps 60

# Ensure good network bandwidth
```

### For Many Clients
```bash
# Host: Lower FPS and resolution
python host.py --fps 30 --max-clients 4

# Monitor network bandwidth
```

## Finding Your Host IP Address

### Method 1: From CouchController Output
- The host application displays its IP when it starts

### Method 2: Command Line
```bash
# Windows
ipconfig

# Look for "IPv4 Address" under your active network adapter
# Usually starts with 192.168.x.x or 10.x.x.x
```

### Method 3: Windows Settings
1. Open Settings → Network & Internet
2. Click your connection (Wi-Fi or Ethernet)
3. Scroll down to "Properties"
4. Find "IPv4 address"

## Next Steps

Once you have everything working:

1. Test with a simple local multiplayer game
2. Experiment with FPS and quality settings
3. Try different network configurations
4. Consider creating shortcuts for easy launching

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Enable debug mode: `python host.py --debug`
3. Check the logs for error messages
4. Verify all prerequisites are installed

Enjoy your network-enabled couch co-op gaming!
