# Quick Start Guide

Get up and running with CouchController in 5 minutes.

## Prerequisites Check

Before starting:
- [ ] Windows 10/11 on host and clients
- [ ] Python 3.8+ installed
- [ ] Controllers connected to client machines
- [ ] All machines on same network

## Installation (5 minutes)

### On Host Machine

```bash
# 1. Install Python packages
cd couchcontroller
pip install -r requirements.txt

# 2. Download and install ViGEmBus driver
# Visit: https://github.com/ViGEm/ViGEmBus/releases
# Download: ViGEmBus_Setup_x64.exe
# Run as Administrator and restart

# 3. Test installation
couchcontroller-test
```

### On Client Machine(s)

```bash
# 1. Install Python packages
cd couchcontroller
pip install -r requirements.txt

# 2. Connect controller

# 3. Test installation
couchcontroller-test
```

## First Test (Without Game)

### Step 1: Start Host

On the host machine:

```bash
couchcontroller-host
```

You should see:
```
============================================================
HOST READY!
============================================================
Monitor: 1
Target FPS: 60
Max clients: 4

Clients can connect with:
  couchcontroller-client --host 192.168.1.100

Press Ctrl+C to stop
============================================================
```

**Note the IP address!** (e.g., `192.168.1.100`)

### Step 2: Start Client

On a client machine, using the IP from above:

```bash
couchcontroller-client --host 192.168.1.100
```

You should see:
```
============================================================
CLIENT READY!
============================================================
Connected to: 192.168.1.100
Controller: Xbox Controller
Assigned slot: 0

Press ESC or close window to disconnect
============================================================
```

### Step 3: Test

- **Client:** Press controller buttons
- **Host:** Open "Set up USB game controllers" in Windows
  - Search for "Game Controllers" in Start menu
  - You should see a virtual Xbox controller
  - Click "Properties" and verify it responds to client's button presses

If buttons light up on the host when you press them on the client: **Success!**

### Setup

1. **Start CouchController FIRST**
   ```bash
   # Host
   couchcontroller-host

   # Clients (on other machines)
   couchcontroller-client --host <HOST_IP>
   ```

2. **Launch the game on host**

3. **Configure game for local multiplayer**
   - In game settings, enable local co-op
   - Assign players to controllers
   - Client controllers will appear as "Xbox 360 Controller"

4. **Play!**
   - Clients see the host's screen
   - Clients control their assigned player
   - Everyone can play together over the network

## Common Scenarios

### Scenario 1: Two Players, Same Room, Different Machines

**Why:** Each player wants their own screen/setup

```bash
# Host (Player 1's machine)
couchcontroller-host

# Client (Player 2's machine, same room)
couchcontroller-client --host 192.168.1.100 --fullscreen
```

### Scenario 2: Multiple Players, Remote

**Why:** Friends in different locations

```bash
# Host
couchcontroller-host --fps 30  # Lower FPS for better bandwidth

# Clients (remote locations)
couchcontroller-client --host <HOST_IP>
```

**Note:** Requires port forwarding or VPN for internet play.

### Scenario 3: LAN Party

**Why:** Best performance for competitive games

```bash
# Host (wired connection)
couchcontroller-host --fps 60

# Clients (preferably wired)
couchcontroller-client --host <HOST_IP>
```

### Scenario 4: Low-End Client Machine

**Why:** Client machine struggles with video

```bash
# Host (reduce quality)
couchcontroller-host --fps 30

# Client
couchcontroller-client --host <HOST_IP>
```

## Troubleshooting Quick Fixes

### "No controller found" (Client)
```bash
# 1. Connect controller
# 2. Verify in Windows settings (joy.cpl)
# 3. Restart client application
```

### "Connection timeout" (Client)
```bash
# 1. Check host IP: ipconfig
# 2. Verify host is running
# 3. Test ping: ping <HOST_IP>
# 4. Check firewall (temporarily disable to test)
```

### "Game doesn't see controller" (Host)
```bash
# 1. Start CouchController BEFORE game
# 2. Check Windows Game Controllers (joy.cpl)
# 3. Restart game
# 4. Verify ViGEmBus is installed
```

### "Video is choppy" (Client)
```bash
# 1. Use wired Ethernet
# 2. Lower FPS: couchcontroller-host --fps 30
# 3. Close bandwidth-heavy apps
# 4. Check: ping -t <HOST_IP>
```

## Performance Tips

### For Best Experience

1. **Network:**
   - Host: Wired (Ethernet)
   - Clients: 5GHz WiFi or wired

2. **Settings:**
   - Start with default (60 FPS)
   - Lower if laggy (30 FPS)
   - Monitor CPU usage

3. **Environment:**
   - Close unnecessary apps
   - Use LAN, not internet
   - Minimize network traffic

4. **Explore Advanced Features**
   - Debug mode: `--debug`
   - Multiple clients
   - Different monitors

## Example Session

Here's a complete example of a typical session:

```bash
# === HOST (Machine A: 192.168.1.100) ===

# 1. Start CouchController
couchcontroller-host
# Output: HOST READY! Clients can connect to 192.168.1.100

# 2. Launch game (e.g., Overcooked 2)
# 3. Configure for local co-op
# 4. Wait for players to join


# === CLIENT 1 (Machine B) ===

# 1. Connect controller
# 2. Start client
couchcontroller-client --host 192.168.1.100
# Output: CLIENT READY! Assigned slot: 0

# 3. See host's screen in window
# 4. Press controller buttons to test


# === CLIENT 2 (Machine C) ===

# 1. Connect controller
# 2. Start client
couchcontroller-client --host 192.168.1.100 --fullscreen
# Output: CLIENT READY! Assigned slot: 1

# 3. See host's screen fullscreen
# 4. Start playing!


# === IN GAME (On Host) ===

# Assign players:
# - Player 1 (Host): Use host's local controller
# - Player 2 (Client 1): Will show as "Xbox 360 Controller" slot 0
# - Player 3 (Client 2): Will show as "Xbox 360 Controller" slot 1

# Start game and play!
```

## Verification Checklist

Before starting a game session:

**Host:**
- [ ] CouchController running
- [ ] IP address noted
- [ ] Firewall allows connections
- [ ] Game ready to launch

**Client:**
- [ ] Controller connected
- [ ] Can ping host
- [ ] CouchController client running
- [ ] Sees host's screen
- [ ] Controller input works (test in joy.cpl on host)

## Getting Help

If you get stuck:

1. Run tests: `couchcontroller-test`
2. Check logs with debug: `couchcontroller-host --debug`
3. Review SETUP.md for detailed instructions

## Tips for Best Experience

1. **Always start host first** - Virtual controllers need to exist before game launches
2. **Use wired connections** - Even 5GHz WiFi can't beat Ethernet for latency
3. **Test without game first** - Verify everything works before adding game complexity
4. **Monitor network** - Use `ping` to check for latency spikes
5. **Close background apps** - Discord streaming, OBS, etc. can impact performance
