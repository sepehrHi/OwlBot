# 🚀 Getting Started with OwlBot

Complete guide to install, configure, and run OwlBot on your Windows machine.

---

## 📋 Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Windows** — Some modules require Win32 API (audio, keyboard, WMI)
- **FFmpeg** (optional) — Required for voice playback and video recording
  - Install via [WinGet](https://winget.run/): `winget install Gyan.FFmpeg`
  - Or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **Telegram Bot Token** — Get one from [@BotFather](https://t.me/BotFather)

---

## 📦 Installation

### From PyPI (Recommended)

```bash
# Full installation with all features (Windows + cross-platform)
pip install owlbot-remote[all]

# Cross-platform only (no audio, no keyboard, no WMI)
pip install owlbot-remote

# Development installation
pip install -e .[dev]
```

### From Source

```bash
git clone https://github.com/sepehrHi/OwlBot.git
cd OwlBot
pip install -e .[all]
```

---

## ⚙️ Configuration

### Quick Configuration

Create a file named `config.py`:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="YOUR_BOT_TOKEN_HERE",           # Get from @BotFather
    authorized_users=[123456789],           # Your Telegram user ID(s)
    modules=[
        "system", "screen", "files",
        "input", "processes", "monitoring",
        "audio", "network"
    ],
    log_level="INFO",
    log_file="owlbot.log",
    enable_logging=True,
)
```

### Using CLI

```bash
# Basic usage
owlbot --token YOUR_BOT_TOKEN --users 123456789,987654321

# With options
owlbot --token TOKEN --users 123456789 \
  --modules system,screen,files,input,processes,monitoring,audio,network \
  --log-level DEBUG --no-log-file
```

### Finding Your Telegram User ID

1. Open Telegram and message [@userinfobot](https://t.me/userinfobot)
2. It will reply with your numeric User ID
3. Add that number to `authorized_users`

---

## 🏃 Running OwlBot

### As a Python Script

```python
from owlbot import OwlBot

bot = OwlBot(
    token="YOUR_TOKEN",
    authorized_users=[YOUR_USER_ID],
    modules=["system", "screen", "files", "processes", "monitoring"],
)
bot.run()
```

```bash
python your_bot.py
```

### As a Windows Service (Recommended for 24/7)

Create a service using [NSSM](https://nssm.cc/):

```cmd
nssm install OwlBot
# Path: python.exe
# Arguments: C:\path\to\your_bot.py
# Startup directory: C:\path\to
nssm start OwlBot
```

---

## 🎮 Basic Commands

Once running, message your bot on Telegram:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | System status (CPU, RAM, Disk, Battery) |
| `/screenshot` | Capture desktop screenshot |
| `/webcam` | Capture webcam photo |
| `/listdir` | List files in current directory |
| `/getfile <path>` | Download a file |
| `/tasklist` | List running processes |
| `/killtask <name>` | Kill a process by name |
| `/monitor cpu` | Start CPU monitoring alerts |
| `/ping` | Health check |

Type `/help` anytime to see all available commands for your loaded modules.

---

## 🔧 Module Configuration

Enable only the modules you need:

```python
# Minimal (cross-platform)
modules = ["system", "files", "processes"]

# Full Windows control
modules = [
    "system", "screen", "files", "input",
    "processes", "monitoring", "audio", "network"
]
```

| Module | Platform | Dependencies |
|--------|----------|--------------|
| `system` | Cross-platform | `psutil` |
| `screen` | Cross-platform | `pyautogui`, `opencv-python` |
| `files` | Cross-platform | — |
| `input` | Windows only | `pyautogui`, `keyboard` |
| `processes` | Cross-platform | `psutil` |
| `monitoring` | Cross-platform | `psutil` |
| `audio` | Windows only | `pycaw`, `pyaudio` |
| `network` | Windows only | `pywifi` |

---

## 🔐 Security Best Practices

1. **Never commit your token** — Use environment variables:
   ```python
   import os
   token = os.getenv("OWLBOT_TOKEN")
   ```

2. **Restrict authorized users** — Only add trusted Telegram IDs

3. **Run with least privilege** — Don't run as Administrator unless needed

4. **Monitor logs** — Check `owlbot.log` for suspicious activity

---

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Reinstall with all extras
pip install --force-reinstall owlbot-remote[all]
```

### FFmpeg not found

```bash
winget install Gyan.FFmpeg
# Then restart your terminal
```

### Permission denied (Windows)

- Run terminal as Administrator
- Or add user to "Performance Monitor Users" group for monitoring

### Module load failures

Check logs: `tail -f owlbot.log`

---

## 📚 Next Steps

- [Configuration Reference](CONFIGURATION.md)
- [Module Reference](MODULES.md)
- [CLI Reference](CLI.md)
- [Development Guide](DEVELOPMENT.md)
- [Security Guide](SECURITY.md)