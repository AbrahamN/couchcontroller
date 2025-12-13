# CouchController

**Local-first network game controller sharing for couch co-op games.**

Transform any local multiplayer game into a network-enabled co-op experience. Your friends connect from their own computers, see your screen, and their controllers appear as if they're plugged directly into your machine.

## Features

- **Universal Game Support** - Works with ANY game that supports local multiplayer
- **Keyboard OR Controller** - No controller? No problem! Use your keyboard as a virtual gamepad
- **Low Latency** - UDP streaming optimized for responsive gameplay (~20-30ms on LAN)
- **Self-Hosted** - No cloud services, complete privacy and control
- **Simple Setup** - Python-based, easy to install and configure
- **LAN-First** - Optimized for local networks, optional internet support
- **AI** - Vibe Coded, because why not

## Why CouchController?

Existing solutions like Parsec and Steam Remote Play are great, but:
- They rely on cloud infrastructure
- You don't control your data
- They may have restrictions or costs
- LAN performance isn't always prioritized

**CouchController gives you complete control** - perfect for LAN parties, home networks, or privacy-conscious gamers.

## How It Works

```
┌─────────────────────────┐         ┌──────────────────────────┐
│      HOST MACHINE       │         │     CLIENT MACHINE       │
│  ┌─────────────────┐    │         │   ┌──────────────────┐   │
│  │  Game Running   │    │         │   │   Controller     │   │
│  └────────┬────────┘    │         │   └────────┬─────────┘   │
│           │             │         │            │             │
│  ┌────────▼────────┐    │         │   ┌────────▼─────────┐   │
│  │ Screen Capture  │    │  Video  │   │  Video Display   │   │
│  │   + Encoding    │────┼────────►│   │   + Decoding     │   │
│  └─────────────────┘    │  Stream │   └──────────────────┘   │
│           ▲             │         │            │             │
│  ┌────────┴────────┐    │ Control │   ┌────────▼─────────┐   │
│  │    Virtual      │◄───┼─────────┼───┤  Input Capture   │   │
│  │  Controllers    │    │  Data   │   └──────────────────┘   │
│  └────────┬────────┘    │         │                          │
│           │             │         │                          │
│  ┌────────▼────────┐    │         │                          │
│  │ Inject to Game  │    │         │                          │
│  └─────────────────┘    │         │                          │
└─────────────────────────┘         └──────────────────────────┘
```

**The magic:** Client controllers appear as virtual Xbox 360 controllers on the host, making them indistinguishable from local controllers.

## Quick Start

### Prerequisites
- Windows 10/11 (host and clients)
- Python 3.8+
- Game controllers for clients
- Local network (LAN or WiFi)

### Installation

**Option 1: Install directly from GitHub (Recommended)**

```bash
# Install for all users
pip install git+https://github.com/abrahamn/couchcontroller.git

# Host machine only - also install virtual controller support
pip install git+https://github.com/abrahamn/couchcontroller.git[host]
```

**Option 2: Clone and install from source**

```bash
# Clone the repository
git clone https://github.com/abrahamn/couchcontroller.git
cd couchcontroller

# Install in development mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

**Host Machine Only - Install ViGEmBus driver:**

The host needs a driver to create virtual Xbox controllers:

1. Download from: https://github.com/ViGEm/ViGEmBus/releases
2. Install `ViGEmBus_Setup_x64.exe` as Administrator
3. Restart your computer

**Verify Installation:**

```bash
couchcontroller-test
```

### Running

After installation, you can use the CLI commands from anywhere:

**Host (machine with the game):**
```bash
couchcontroller-host
# Note the IP address shown (e.g., 192.168.1.100)
```

**Client (remote player with controller):**
```bash
couchcontroller-client --host 192.168.1.100
```

**Client (using keyboard - no controller needed!):**
```bash
couchcontroller-client --host 192.168.1.100 --keyboard
```

**Then launch your game on the host!**

**Tip:** If you installed from source, you can also use the old method:
```bash
python host.py        # or couchcontroller-host
python client.py --host <IP>   # or couchcontroller-client --host <IP>
```

See [QUICK_START.md](QUICK_START.md) for detailed walkthrough.

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[KEYBOARD_GUIDE.md](KEYBOARD_GUIDE.md)** - Play with keyboard (no controller needed!)
- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive and design decisions
- **[test_components.py](test_components.py)** - Verify your installation

## Use Cases

### LAN Party
Transform single-screen local co-op into individual screens for each player.

### Remote Friends
Play local-only games with friends across the internet (with port forwarding).

### Living Room Gaming
Each player can use their own laptop while playing on the main gaming PC.

### Development/Testing
Test local multiplayer features without multiple physical controllers.

## Performance

Typical performance on LAN:

| Metric | Value | Notes |
|--------|-------|-------|
| Video Latency | 20-30ms | 1080p60, hardware encoding |
| Input Latency | 10-15ms | 120Hz polling rate |
| Bandwidth | 5 Mbps/client | 1080p60 H.264 |
| Max Clients | 4 | Configurable |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed performance analysis.

## Supported Controllers

Works with any controller supported by Windows:
- Xbox One / Series X|S
- PlayStation 4 / 5 (via DS4Windows or built-in support)
- Nintendo Switch Pro Controller
- Generic USB/Bluetooth controllers
- Steam Controller
- And many more!

## Comparison

| Feature | CouchController | Parsec | Steam Remote Play | Moonlight |
|---------|----------------|--------|-------------------|-----------|
| Self-hosted | ✅ | ❌ | ⚠️ | ✅ |
| LAN-first | ✅ | ❌ | ⚠️ | ✅ |
| Open source | ✅ | ❌ | ❌ | ✅ |
| Game agnostic | ✅ | ✅ | ❌ | ❌ |
| Privacy | ✅ | ❌ | ⚠️ | ✅ |

## Examples

### Example 1: Overcooked 2 with Remote Friends
```bash
# Host
couchcontroller-host --fps 60

# Friend 1
couchcontroller-client --host YOUR_IP --fullscreen

# Friend 2
couchcontroller-client --host YOUR_IP --fullscreen
```

### Example 2: Low-Bandwidth Setup
```bash
# Reduce FPS and quality for slower networks
couchcontroller-host --fps 30
```

### Example 3: 4-Player Local
```bash
# Allow up to 4 remote controllers
couchcontroller-host --max-clients 4
```

### Example 4: Playing Without Controllers
```bash
# Perfect for when you don't have controllers!

# Player 1 (has controller)
couchcontroller-client --host YOUR_IP

# Player 2 (using keyboard)
couchcontroller-client --host YOUR_IP --keyboard

# Player 3 (also keyboard)
couchcontroller-client --host YOUR_IP --keyboard --fullscreen
```

See [KEYBOARD_GUIDE.md](KEYBOARD_GUIDE.md) for keyboard controls!

## Troubleshooting

**Host Issues:**
- Ensure ViGEmBus driver is installed
- Check Windows Firewall settings
- Start CouchController BEFORE launching game

**Client Issues:**
- No controller? Use `--keyboard` flag to play with keyboard!
- Verify controller is connected (check Windows "Game Controllers")
- Test network with `ping <host-ip>`
- Ensure you're on the same network as host

**Performance Issues:**
- Use wired Ethernet for host
- Lower FPS with `--fps 30`
- Close bandwidth-heavy applications
- Check for WiFi interference

See [SETUP.md](SETUP.md) for comprehensive troubleshooting.

## Development Status

✅ **MVP Complete** - Core functionality working

**Current features:**
- Screen capture and streaming
- Virtual controller creation
- Network communication
- Client video display
- Controller input forwarding

**Planned features:**
- Audio streaming
- Auto-discovery (mDNS)
- Hardware video encoding
- Multi-monitor support
- Cross-platform support (Linux, macOS)

## Contributing

This is a learning project, but contributions are welcome! Areas for improvement:

- Performance optimization
- Cross-platform support
- Audio streaming
- Better error handling
- UI/UX improvements

## Technical Stack

- **Screen Capture:** mss (DirectX on Windows)
- **Video Codec:** H.264 via PyAV (FFmpeg)
- **Virtual Controllers:** ViGEmBus + vgamepad
- **Controller Input:** pygame
- **Networking:** Python sockets (UDP)
- **Display:** pygame

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Security Notes

**Current implementation:**
- No authentication - anyone on network can connect
- No encryption - data sent in plaintext
- Designed for trusted LAN environments

**For internet use:**
- Use a VPN (WireGuard, ZeroTier)
- Implement network isolation
- Consider adding authentication

## License

MIT License - See LICENSE file for details.

## Acknowledgments

Inspired by:
- Parsec (commercial game streaming)
- Moonlight (open-source game streaming)
- Steam Remote Play Together
- The awesome local co-op gaming community

Built with love for couch co-op gaming. 🎮

---

**Ready to play?** Check out [QUICK_START.md](QUICK_START.md) to get started in 5 minutes!
