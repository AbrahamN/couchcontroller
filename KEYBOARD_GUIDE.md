# Keyboard Controls Guide

Don't have a game controller? No problem! CouchController lets you use your keyboard as a virtual Xbox controller.

## Quick Start

Just add `--keyboard` when connecting:

```bash
couchcontroller-client --host 192.168.1.100 --keyboard
```

That's it! Your keyboard now acts as an Xbox 360 controller.

## Default Keyboard Mapping

### Movement & Camera

| Keys | Function | Xbox Equivalent |
|------|----------|-----------------|
| **W/A/S/D** | Movement | Left Stick |
| **Arrow Keys** | Camera/Look | Right Stick |

### Action Buttons

| Key | Function | Xbox Equivalent |
|-----|----------|-----------------|
| **J** | Jump/Accept | A Button |
| **K** | Back/Cancel | B Button |
| **I** | Left Action | X Button |
| **L** | Top Action | Y Button |

### Triggers & Bumpers

| Key | Function | Xbox Equivalent |
|-----|----------|-----------------|
| **Q** | Left Trigger | LT |
| **E** | Right Trigger | RT |
| **1** | Left Bumper | LB |
| **2** | Right Bumper | RB |

### D-Pad

| Keys | Function | Xbox Equivalent |
|------|----------|-----------------|
| **Numpad 8/4/2/6** | Up/Left/Down/Right | D-Pad |

### Menu & System

| Key | Function | Xbox Equivalent |
|-----|----------|-----------------|
| **Enter** | Start/Pause | Start Button |
| **Backspace** | Back/Select | Back Button |
| **Left Shift** | Sprint/Run | Left Stick Press (L3) |
| **Right Shift** | Crouch/Special | Right Stick Press (R3) |
| **ESC** | Disconnect | - |

## Visual Layout

```
Keyboard Layout for Gaming:
┌─────────────────────────────────────────────────────┐
│                                                     │
│    [1]LB  [2]RB                  [I]X    [L]Y      │
│    [Q]LT  [E]RT                  [J]A    [K]B      │
│                                                     │
│         [W]                                         │
│    [A] [S] [D]     Movement (Left Stick)           │
│                                                     │
│                            [↑]                      │
│                       [←] [↓] [→]  Camera (Right)   │
│                                                     │
│    [LShift] Sprint              [RShift] Crouch    │
│                                                     │
│    [Backspace] Back             [Enter] Start      │
│                                                     │
│    Numpad: [8]                                     │
│         [4][6]  D-Pad                              │
│            [2]                                      │
│                                                     │
│    [ESC] Disconnect                                │
└─────────────────────────────────────────────────────┘
```

## Why This Layout?

**WASD + Arrow Keys:**
- WASD is universal for movement
- Arrow keys are natural for camera control
- Your hands stay in home position

**IJKL for Buttons:**
- Right hand stays on home row
- J is under index finger (A button - most used)
- Easy to reach all four face buttons

**Q/E for Triggers:**
- Natural finger positions
- Common in FPS games
- Easy to hold while moving (WASD)

**1/2 for Bumpers:**
- Above Q/E (triggers)
- Easy to tap quickly

## Tips for Keyboard Play

### For Platformers (Mario, Celeste, etc.)
- Main controls: **WASD** + **J** (jump)
- Sprint: **Q** or **LShift**
- Works great! Digital input is actually better for precise platforming

### For Fighting Games (Street Fighter, etc.)
- Movement: **WASD** or **Arrow Keys**
- Buttons: **I/J/K/L** for punches/kicks
- D-Pad: **Numpad** for special moves
- Perfect for combos!

### For Racing Games
- Steering: **A/D**
- Gas/Brake: **W/S**
- Boost: **Q** or **E**
- Handbrake: **Space** (if supported)

### For Shooters (if controller-based)
- Move: **WASD**
- Look: **Arrow Keys**
- Shoot: **J** (A button)
- Aim: **I** (X button) or **E** (RT)
- Works, but mouse+keyboard is better for FPS!

### For RPGs/Adventure Games
- Move: **WASD**
- Interact: **J** (A)
- Menu: **Enter** (Start)
- Camera: **Arrow Keys**
- Excellent for turn-based or slower-paced games

## Limitations

**What Works:**
- ✅ All buttons and inputs
- ✅ D-Pad directions
- ✅ Triggers (on/off)
- ✅ Perfect for most games!

**What's Different:**
- ⚠️ Analog sticks are digital (8 directions, not full 360°)
- ⚠️ Triggers are on/off (no pressure sensitivity)
- ⚠️ Can't do subtle movements (walk vs run)

**Best For:**
- Platformers
- Fighting games
- Turn-based RPGs
- Puzzle games
- 2D games
- Retro-style games

**Not Ideal For:**
- Racing simulators (need analog steering)
- Stealth games (need slow movement)
- Games requiring fine analog control

## Advanced: Diagonal Movement

When pressing two movement keys at once:
- **W+A** = Up-Left (full analog value)
- **W+D** = Up-Right
- **S+A** = Down-Left
- **S+D** = Down-Right

The mapper automatically converts these to proper diagonal stick positions!

## Troubleshooting

### Keys Not Working?

1. **Make sure the CouchController window has focus**
   - Click on the video window
   - Keys only work when window is active

2. **Check Num Lock for D-Pad**
   - Num Lock must be ON for numpad D-Pad
   - Use arrow keys instead if needed

3. **Some Keys Stuck?**
   - Alt+Tab away and back
   - Windows might have captured the key

### Prefer Different Keys?

The mapping is designed to be intuitive, but if you want to customize it, you can modify:
```python
# In couchcontroller/client/keyboard_input.py
# Look for DEFAULT_MAPPING and change key assignments
```

We may add custom key mapping in a future update!

## Comparison: Keyboard vs Controller

| Feature | Controller | Keyboard |
|---------|-----------|----------|
| Analog Movement | ✅ 360° smooth | ⚠️ 8 directions |
| Precise Input | ⚠️ Stick drift | ✅ Perfect |
| Speed | ⚠️ Slower input | ✅ Lightning fast |
| Comfort | ✅ Ergonomic | ⚠️ Depends |
| Cost | ❌ Need to buy | ✅ You have one |
| Setup | ⚠️ Drivers, pairing | ✅ Just works |

## Examples

### Example 1: Join with Keyboard (No Controller)
```bash
# You don't have a controller? Use keyboard!
couchcontroller-client --host 192.168.1.100 --keyboard

# Fullscreen for immersion
couchcontroller-client --host 192.168.1.100 --keyboard --fullscreen
```

### Example 2: Mix and Match
```bash
# Player 1: Controller
couchcontroller-client --host 192.168.1.100

# Player 2: Keyboard (no controller needed!)
couchcontroller-client --host 192.168.1.100 --keyboard
```

### Example 3: Everyone Uses Keyboards
```bash
# Perfect for LAN parties when you don't have 4 controllers
# Player 1, 2, 3, 4 all connect with keyboards

couchcontroller-client --host 192.168.1.100 --keyboard
```

## Getting Started

1. **Start the client with keyboard:**
   ```bash
   couchcontroller-client --host <HOST_IP> --keyboard
   ```

2. **When it starts, you'll see the key mapping printed**

3. **The window will show the host's screen**

4. **Press keys to play!**
   - Use **WASD** to move around
   - Press **J** to jump/interact
   - Use **Arrow Keys** to look around

5. **Press ESC to disconnect when done**

## Accessibility

Keyboard controls make CouchController accessible to:
- **Players without controllers** - No need to buy hardware
- **Budget gamers** - Controllers can be expensive
- **LAN parties** - Not everyone brings controllers
- **Quick testing** - Jump in without setup
- **Laptop players** - Built-in keyboard works great

## Did You Know?

Many speedrunners and competitive players prefer keyboards for:
- **Frame-perfect inputs** - No analog delay
- **Instant direction changes** - Digital is faster
- **Precision** - Exact inputs every time
- **Muscle memory** - Touch typing skills transfer

## Future Enhancements

Coming soon (maybe!):
- [ ] Custom key mapping UI
- [ ] Save/load key profiles
- [ ] Alternative preset layouts
- [ ] Visual on-screen key display
- [ ] Gamepad overlay showing pressed buttons

## Feedback

Using keyboard controls? Let us know how it works for you!
- What games did you try?
- Which layout would you prefer?
- Any key conflicts?

Open an issue on GitHub: https://github.com/abrahamn/couchcontroller/issues

---

**Happy gaming with your keyboard!** ⌨️🎮
