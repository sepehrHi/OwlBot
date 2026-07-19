# 🧩 Module Reference

Complete reference for all OwlBot modules — commands, features, and platform requirements.

---

## 📋 Quick Module Selection

```python
# Minimal cross-platform
modules = ["system", "files", "processes", "monitoring"]

# Full cross-platform
modules = ["system", "screen", "files", "processes", "monitoring"]

# Full Windows control
modules = [
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring",
    "network", "ffmpeg"
]
```

| Module | Cross-Platform | Windows Only | Key Dependencies |
|--------|---------------|--------------|------------------|
| `system` | ✅ | — | `psutil` |
| `screen` | ✅ | — | `pyautogui`, `opencv-python`, `numpy` |
| `files` | ✅ | — | — |
| `input` | — | ✅ | `pyautogui`, `keyboard` |
| `processes` | ✅ | — | `psutil` |
| `monitoring` | ✅ | — | `psutil` |
| `audio` | — | ✅ | `pycaw`, `pyaudio` |
| `network` | — | ✅ | `pywifi` |
| `ffmpeg` | — | ✅ | FFmpeg binary |
| `ip` | ✅ (GPS fix Windows-only) | — | `requests` |

---

## 🖥️ System Module

**Platform**: Cross-platform  
**Dependencies**: `psutil`  
**Module class**: `SystemModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/status` | `/sys`, `/info` | Complete system status | — |
| `/uptime` | — | System uptime | — |
| `/ping` | — | Bot health check | — |
| `/lock` | — | Lock workstation (Windows) | — |
| `/shutdown` | — | Shutdown PC (confirmation) | — |
| `/restart` | — | Restart PC (confirmation) | — |

### Features

- **CPU**: Usage per core, frequency, temperature (if available)
- **Memory**: Total, used, free, swap
- **Disk**: Per-partition usage, I/O counters
- **Network**: Per-interface bytes sent/received, speed
- **Battery**: Percentage, status, time remaining (laptops)
- **Power**: Shutdown/restart/lock with confirmation prompts

### Example Output

```
/status

🖥️ SYSTEM STATUS
━━━━━━━━━━━━━━━━━━━━━━
💻 CPU: AMD Ryzen 9 5900X (12 cores)
   Usage: ██████████░░ 34%
   Temp: 48°C

🧠 RAM: 64.0 GB
   Used: ████████████░░ 42.3 GB (66%)
   Free: 21.7 GB

💾 Disk C::
   Used: ██████████████░░ 850 GB / 1.8 TB (47%)

🔋 Battery: 92% — Charging
🌐 Network: ↑ 2.1 MB/s  ↓ 15.4 MB/s
⏱️ Uptime: 5d 3h 14m
```

### Platform Notes

- **Windows**: All features + lock/shutdown/restart
- **Linux/macOS**: All features except lock/shutdown/restart (use `/cmd systemctl poweroff`)

---

## 📸 Screen Module

**Platform**: Cross-platform  
**Dependencies**: `pyautogui`, `opencv-python`, `numpy`  
**Module class**: `ScreenModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/screenshot` | `/sc`, `/ss` | Capture full screen | — |
| `/webcam` | `/cam` | Capture webcam photo | — |
| `/timelapse` | `/tl` | Timelapse screenshots | `<interval> <count>` |
| `/startstream` | `/stream` | Start screen streaming | — |
| `/stopstream` | — | Stop stream & send video | — |

### Parameters

```bash
# Timelapse: interval seconds, count frames
/timelapse 10 30   # 30 screenshots, 10s apart = 5 minutes
/timelapse 5 60    # 60 screenshots, 5s apart = 5 minutes
```

### Features

- **Multi-monitor**: Captures all monitors stitched horizontally
- **Webcam**: Auto-detects first available camera (index 0)
- **Streaming**: Records MP4 via FFmpeg (requires FFmpeg in PATH)
- **Quality**: Configurable JPEG quality (default 85% screenshots, 50% stream)

### Example Usage

```
/screenshot
→ Sends screenshot.png (full resolution PNG)

/webcam
→ Sends webcam.jpg (640x480 default)

/timelapse 30 20
→ Captures 20 screenshots over 10 minutes
→ Sends timelapse.mp4 (compiled video)

/startstream
→ Starts streaming (5 FPS default)
→ Sends periodic photo updates

/stopstream
→ Stops stream, compiles and sends stream.mp4
```

### Platform Notes

- **Windows**: Full support (DIB, D3D capture)
- **Linux**: Requires X11/Wayland display (`export DISPLAY=:0`)
- **macOS**: Requires accessibility permissions for pyautogui
- **Headless**: Use Xvfb: `Xvfb :99 -screen 0 1920x1080x24 & export DISPLAY=:99`

---

## 📁 Files Module

**Platform**: Cross-platform  
**Dependencies**: None (stdlib)  
**Module class**: `FilesModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/listdir` | `/ls`, `/dir` | List directory | `[path]` |
| `/getfile` | `/download`, `/dl` | Download file | `<path>` |
| `/download` | `/dlurl` | Download from URL | `<url> [dest]` |
| `/hide` | — | Hide file/folder (Win) | `<path>` |
| `/show` | — | Unhide file/folder (Win) | `<path>` |
| `/file` | — | File operations | `<op> <src> [dst]` |

### File Operations

```bash
/file copy <source> <destination>
/file move <source> <destination>
/file delete <path>
/file mkdir <path>
/file rename <old> <new>
```

### Features

- **Directory listing**: Shows size, type, permissions, modified time
- **File download**: Streams large files in chunks (respects `max_file_size_mb`)
- **URL download**: Downloads to PC, notifies on completion
- **Windows attributes**: Hide/show using `attrib +h/-h`
- **Safety**: Path traversal protection, size limits

### Example Output

```
/listdir C:\Users\Sepehr\Documents

📁 C:\Users\Sepehr\Documents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 project.py          12.4 KB  2024-01-15 10:30
📄 notes.txt           2.1 KB   2024-01-14 18:22
📁 Projects            (dir)   2024-01-10 09:15
📁 Archives            (dir)   2024-01-01 12:00
🖼️ screenshot.png     3.2 MB   2024-01-15 14:20

Total: 5 items (2 files, 3 dirs) — 3.2 MB
```

### Size Limits

| Operation | Default Limit | Config |
|-----------|--------------|--------|
| Send file | 50 MB | `max_file_size_mb` |
| Download URL | 20 MB | `max_download_mb` |
| Timelapse frames | 60 | `max_timelapse_count` |

---

## ⌨️ Input Module

**Platform**: Windows only  
**Dependencies**: `pyautogui`, `keyboard`  
**Module class**: `InputModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/type` | — | Type text | `<text>` |
| `/move` | — | Move mouse | `<x> <y>` |
| `/mousepos` | `/mp` | Get mouse position | — |
| `/mouse` | — | Mouse actions | `<action> [params]` |
| `/hotkey` | `/hk` | Send hotkey | `<key+key>` |
| `/msg` | `/msgbox` | Message box | `<text> [title]` |

### Mouse Actions

```bash
/mouse click left|right|middle
/mouse doubleclick
/mouse scroll up|down [clicks]
/mouse drag <x1> <y1> <x2> <y2>
```

### Hotkey Format

```bash
/hotkey ctrl+c
/hotkey alt+tab
/hotkey win+d
/hotkey ctrl+shift+esc
/hotkey f11
```

### Features

- **Text typing**: Simulates keystrokes with configurable delay
- **Mouse control**: Absolute positioning, clicks, scroll, drag
- **Hotkeys**: Any key combination supported by `keyboard` library
- **Message boxes**: Native Windows `MessageBoxW` dialogs

### Example Usage

```
/type Hello, World!
→ Types text at current cursor position

/move 1000 500
→ Moves mouse to (1000, 500)

/mouse click right
→ Right-clicks at current position

/hotkey ctrl+shift+esc
→ Opens Task Manager

/msg "Task completed!" "OwlBot"
→ Shows message box with title "OwlBot"
```

### Safety Notes

- Requires Windows (Win32 API via `pyautogui`/`keyboard`)
- Some actions may trigger UAC prompts
- Run as Administrator for system-level hotkeys

---

## ⚙️ Processes Module

**Platform**: Cross-platform  
**Dependencies**: `psutil`  
**Module class**: `ProcessesModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/tasklist` | `/ps`, `/tasks` | List processes | `[limit]` |
| `/killtask` | `/kill` | Kill process | `<name>` |
| `/run` | — | Launch program | `<program> [args]` |
| `/cmd` | `/shell` | Shell command | `<command>` |
| `/script` | `/py` | Inline Python | `<code>` |
| `/runscript` | — | Run Python file | `<path>` |

### Tasklist Output

```
/tasklist 15

⚙️ TOP 15 PROCESSES BY CPU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
chrome.exe           15.2%  1.2 GB  4520
python.exe            8.1%  245 MB  8840
code.exe              5.3%  980 MB  3120
dwm.exe               2.1%  180 MB  2840
explorer.exe          1.0%  210 MB  4120
...
Total: 287 processes
```

### Features

- **Process listing**: Sorted by CPU, shows PID, memory, name
- **Kill by name**: Case-insensitive, kills all matching processes
- **Protected processes**: System processes cannot be killed (configurable)
- **Execution**: `/run` for programs, `/cmd` for shell, `/script` for Python
- **Safety**: Confirmation for dangerous operations

### Protected Processes (Default)

```
system, svchost.exe, csrss.exe, winlogon.exe,
lsass.exe, services.exe, smss.exe, wininit.exe,
dwm.exe, ntoskrnl.exe
```

### Example Usage

```
/tasklist 10
→ Shows top 10 processes

/killtask notepad.exe
→ Kills all notepad.exe instances

/run "C:\Program Files\Notepad++\notepad++.exe"
→ Launches Notepad++

/cmd ipconfig /all
→ Runs command, returns output

/script import os; print(os.getcwd())
→ Executes inline Python

/runscript C:\scripts\backup.py
→ Runs Python file
```

---

## 📊 Monitoring Module

**Platform**: Cross-platform  
**Dependencies**: `psutil`  
**Module class**: `MonitoringModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/monitor` | `/mon` | Start monitoring | `<type>` |
| `/stopmonitor` | `/stopmon` | Stop monitoring | — |

### Monitor Types

```bash
/monitor cpu     # CPU usage alerts (>80%)
/monitor ram     # RAM usage alerts (>85%)
/monitor disk    # Disk usage alerts (>90%)
/monitor temp    # CPU temp alerts (>80°C)
/monitor all     # All of the above
```

### Alert Format

```
⚠️ MONITOR ALERT — CPU
━━━━━━━━━━━━━━━━━━━━━━━
Current: 92% (threshold: 80%)
Time: 2024-01-15 14:32:10
Host: DESKTOP-ABC123
```

### Features

- **Periodic checks**: Configurable interval (default 10s)
- **Thresholds**: Fixed defaults, customizable via config
- **Multi-type**: Run multiple monitors simultaneously
- **Cooldown**: 60s cooldown between same-type alerts

### Configuration

```python
BotConfig(
    ...,
    monitor_interval=5,  # Check every 5 seconds
)
```

---

## 🔊 Audio Module

**Platform**: Windows only  
**Dependencies**: `pycaw`, `pyaudio`  
**Module class**: `AudioModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/mute` | — | Mute system volume | — |
| `/unmute` | — | Unmute system volume | — |
| `/volume` | `/vol` | Set volume | `<0-100>` |
| `/startrec` | `/rec` | Start recording | `[seconds]` |
| `/stoprec` | — | Stop recording & send | — |
| `/playvoice` | — | Toggle voice playback | — |

### Features

- **System volume**: Controls default audio endpoint (via `pycaw`)
- **Recording**: Microphone capture to WAV (via `pyaudio`)
- **Voice playback**: Plays incoming voice messages through speakers
- **Duration limits**: Configurable min/max recording time

### Example Usage

```
/volume 50
→ Sets system volume to 50%

/mute
→ Mutes all audio

/startrec 30
→ Records microphone for 30 seconds

/stoprec
→ Stops recording, sends audio file

/playvoice
→ Toggles auto-play of incoming voice messages
```

### Configuration

```python
BotConfig(
    ...,
    audio_sample_rate=44100,    # CD quality
    audio_channels=2,           # Stereo
    max_record_duration=300,    # 5 minutes max
    min_record_duration=1,      # 1 second min
)
```

---

## 🌐 Network Module

**Platform**: Windows only  
**Dependencies**: `pywifi`  
**Module class**: `NetworkModule`

### Commands

| Command | Aliases | Description | Parameters |
|---------|---------|-------------|------------|
| `/netcheck` | `/pingnet` | Internet connectivity | — |
| `/wifiscan` | `/wifi` | Scan Wi-Fi networks | — |
| `/clipboard` | `/cb` | Clipboard operations | `get` \| `set <text>` |

### Features

- **Connectivity check**: Pings multiple DNS servers
- **Wi-Fi scan**: Lists SSID, signal strength, security
- **Clipboard**: Read/write Windows clipboard

### Example Output

```
/wifiscan

📶 WI-FI NETWORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 HomeNetwork        ████████░░ -45 dBm  WPA2
📱 GuestNetwork       ██████░░░░ -62 dBm  WPA2
🏢 OfficeWiFi         ████░░░░░░ -75 dBm  WPA2-Enterprise
📶 Neighbor1          ██░░░░░░░░ -82 dBm  WPA2
📶 Neighbor2          █░░░░░░░░░ -88 dBm  Open

Total: 5 networks
```

---

## 🌍 IP & Location Module

**Platform**: Cross-platform (real GPS fix is Windows-only, with automatic
IP-based fallback everywhere else)
**Dependencies**: `requests` (already a core dependency — no extras needed)
**Module class**: `IPModule`

> ⚠️ Every command in this module reveals the device's network identity
> and/or approximate physical location. Access is gated by the same
> `authorized_users` allowlist as every other command (e.g. `/shutdown`,
> `/run`) — this module does not widen the trust boundary, it only
> exposes more about a machine you already control. See the
> [Disclaimer](../README.md#-disclaimer) in the main README.

### Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `/myip` | Public + local IP addresses | — |
| `/iplookup` | Geo/ISP lookup for the device's own public IP | — |
| `/iplookup <ip>` | Geo/ISP lookup for an arbitrary IP or hostname | `ip` (IP or hostname) |
| `/vpncheck` | Heuristic VPN/proxy/hosting detection | — |
| `/location` | Send an IP-based location pin to the chat | — |
| `/gps` | Real GPS/Wi-Fi-triangulated fix (Windows), IP fallback otherwise | — |
| `/locationlive <sec>` | Send a Telegram "live location" for N seconds | `sec` (60–86400) |

### Features

- **Public IP**: via `api.ipify.org`
- **Local IPs**: every non-loopback IPv4 address bound to the machine
- **Geo/ISP lookup**: city, region, country, timezone, ISP, org — via `ip-api.com` (free tier, no API key)
- **VPN/proxy detection**: heuristic, based on `ip-api.com`'s `proxy`/`hosting`/`mobile` flags
- **Real GPS**: on Windows, queries `System.Device.Location.GeoCoordinateWatcher`
  (Windows Location Services) for a real GPS or Wi-Fi-triangulated fix;
  requires Location to be enabled in *Settings → Privacy → Location*.
  Falls back automatically to IP-based location if unavailable or denied.
- **Live location**: uses Telegram's native live-location bubble; since
  the "device" is a stationary PC, the pin itself won't move, but the
  live-location UI (countdown, etc.) works as expected.

### Example Output

```
/iplookup 8.8.8.8

🌍  IP Lookup — 8.8.8.8
──────────────────────────────────
📍  Mountain View, California, United States
🏳️  US   ZIP: 94043
🕒  Timezone: America/Los_Angeles
🛰️  Coords: 37.4056, -122.0775
🏢  ISP: Google LLC
🏗️  Org: Google Public DNS
🔌  Proxy/VPN: ✅ No (🏢 hosting/datacenter IP)
```

---

## 🎬 FFmpeg Module

**Platform**: Windows only  
**Dependencies**: FFmpeg binary (auto-installable)  
**Module class**: `FFmpegModule`

### Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `/ffmpeg` | — | Check FFmpeg status |
| `/ffmpeg_install` | — | Download & install FFmpeg |

### Features

- **Auto-detection**: Finds FFmpeg in PATH or common locations
- **Auto-install**: Downloads static build from gyan.dev
- **Version check**: Reports version and capabilities
- **Required for**: Screen streaming, timelapse video, audio conversion

### Example Output

```
/ffmpeg

🎬 FFmpeg STATUS
━━━━━━━━━━━━━━━━━━
Status: ✅ Available
Path: C:\ffmpeg\bin\ffmpeg.exe
Version: 7.0.2-full_build-www.gyan.dev
Codecs: h264, hevc, vp9, aac, mp3, opus
Protocols: file, http, https, rtmp, rtp
```

---

## 🔧 Module Configuration Summary

### Loading Modules

```python
# Python API
bot = OwlBot(
    token=TOKEN,
    authorized_users=[UID],
    modules=["system", "screen", "files", "monitoring"]
)

# CLI
owlbot --token TOKEN --users UID --modules system,screen,files,monitoring
```

### Platform Auto-Detection

```python
# Automatic: Windows-only modules skipped on non-Windows
from owlbot.config import WINDOWS_ONLY_MODULES, CROSS_PLATFORM_MODULES

# On Linux/macOS:
# modules=["system", "screen", "files", "audio", "input"]
# → "audio" and "input" automatically skipped with warning
```

### Module Dependencies Installation

```bash
# Core only
pip install owlbot-remote

# + Screen/Webcam/Stream
pip install owlbot-remote[ui]

# + Windows modules (Audio, Input, Network)
pip install owlbot-remote[windows]

# Everything
pip install owlbot-remote[all]
```

---

## 📦 Creating Custom Modules

```python
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import authorized_only, safe_reply

class MyModule(BaseModule):
    name = "custom"
    description = "My custom commands"
    commands = {
        "hello": "Say hello",
        "calc": "Simple calculator",
    }
    
    @authorized_only
    @safe_reply
    def cmd_hello(self, ctx):
        ctx.reply("Hello from custom module! 👋")
    
    @authorized_only
    @safe_reply
    def cmd_calc(self, ctx):
        try:
            result = eval(ctx.args)  # Be careful!
            ctx.reply(f"🧮 Result: {result}")
        except Exception as e:
            ctx.reply(f"❌ Error: {e}")

# Register
bot = OwlBot(...)
bot.register_module(MyModule)
bot.run()
```

---

## 📚 Related Docs

- [Getting Started](GETTING_STARTED.md)
- [Configuration](CONFIGURATION.md)
- [API Reference](API.md)
- [Examples](EXAMPLES.md)