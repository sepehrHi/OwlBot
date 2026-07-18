# 🦉 OwlBot (owlbot-remote)

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/owlbot-remote.svg)](https://pypi.org/project/owlbot-remote/)
[![CI](https://github.com/sepehrHi/OwlBot/actions/workflows/python-package.yml/badge.svg)](https://github.com/sepehrHi/OwlBot/actions/workflows/python-package.yml)

**OwlBot** is a production‑ready modular remote‑control agent for **Windows**, operated via **Telegram**. It lets you monitor system resources, manage files, control peripherals, capture screen / webcam, and more — all from your phone.

---

## ✨ Features

- 🧩 **100% Modular** — load only the modules you need
- 💉 **Dependency‑Injected** core — ready for extra platforms (Discord, SSH, …)
- 🛡️ **User‑ID whitelisting** and centralized error handling
- 📊 **Live resource monitoring** (CPU, RAM, Disk, temperature)
- 🎹 **Peripheral control** — keyboard, mouse, hotkeys, audio volume
- 📸 **Screen capture, webcam, timelapse, and screen streaming**
- 🔊 **Voice recording, volume control, and incoming‑voice playback**

---

## 🚀 Quick Start

### Prerequisites

- Python **3.11+**
- Windows (some modules require Win32 API)
- `ffmpeg` in `PATH` if you use voice playback (download from [ffmpeg.org](https://ffmpeg.org/))
- A [Telegram Bot Token](https://t.me/BotFather)

### Install from PyPI

```bash
pip install owlbot-remote[all]
```

To install only the cross‑platform subset (no audio, no keyboard, no WMI):

```bash
pip install owlbot-remote
```

### Minimal deployment script

```python
from owlbot import OwlBot

bot = OwlBot(
    token="YOUR_BOT_TOKEN",
    authorized_users=[123456789],       # your Telegram user ID
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

Or via the CLI entry point:

```bash
owlbot --token YOUR_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 Logging

By default OwlBot logs to both the console **and** a rotating‑free log file
(`owlbot.log` in the current directory). All of this is configurable:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="YOUR_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # set to None (or "") to disable the log file only
    enable_logging=True,     # set to False to disable logging entirely
)
```

| Goal | Setting |
|---|---|
| Console + file logging (default) | leave as default |
| Console only, no log file on disk | `log_file=None` |
| Completely silent (no console, no file) | `enable_logging=False` |

The same options are available from the CLI:

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # verbose logging
owlbot --token TOKEN --users 123 --no-log-file        # console only, no file
owlbot --token TOKEN --users 123 --disable-logging    # fully silent
```

---

## 🕹️ Available Modules & Commands

| Module | Command | Description |
|---|---|---|
| **system** | `/status` | CPU, RAM, Disk, Network, Battery |
| | `/uptime` | System uptime |
| | `/ping` | Health‑check |
| | `/lock` | Lock workstation |
| | `/shutdown` | Shut down PC |
| | `/restart` | Reboot PC |
| **screen** | `/screenshot` | Capture desktop |
| | `/webcam` | Capture webcam photo |
| | `/timelapse <s> <n>` | Series of screenshots |
| | `/startstream` | Start screen streaming |
| | `/stopstream` | Stop & send video |
| **input** | `/type <text>` | Type text |
| | `/move <x> <y>` | Move mouse |
| | `/mousepos` | Get mouse position |
| | `/mouse <action>` | Click / scroll / drag |
| | `/hotkey <k1+k2>` | Send hotkey |
| | `/msg <text>` | Show message box |
| **audio** | `/mute` / `/unmute` | Toggle mute |
| | `/volume <0‑100>` | Set volume |
| | `/startrec [sec]` | Record microphone |
| | `/stoprec` | Stop & send recording |
| | `/playvoice` | Toggle incoming‑voice playback |
| **files** | `/listdir [path]` | List directory |
| | `/getfile <path>` | Download file |
| | `/hide` / `/show` | Toggle hidden attribute |
| | `/file copy/move/delete` | File operations |
| **processes** | `/tasklist` | List running processes |
| | `/killtask <exe>` | Kill a process |
| | `/run` / `/cmd` / `/script` | Execute commands |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Periodic alerts |
| | `/stopmonitor` | Stop alerts |
| **network** | `/netcheck` | Check internet connection |
| | `/wifiscan` | Scan Wi‑Fi networks |
| | `/clipboard get\|set` | Read / write clipboard |
| **ffmpeg** | `/ffmpeg` | Check FFmpeg status |
| | `/ffmpeg_install` | Download & install FFmpeg |

---

## 📂 Project Structure

```
owlbot/
├── __init__.py           # Package exports & version
├── config/               # BotConfig dataclass
├── core/
│   ├── bot.py            # Main OwlBot engine
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Shared helpers
├── modules/
│   ├── base.py           # BaseModule interface
│   ├── system.py         # System control
│   ├── screen.py         # Screen/webcam/stream
│   ├── files.py          # File operations
│   ├── processes.py      # Process management
│   ├── input.py          # Keyboard/mouse (Windows)
│   ├── audio.py          # Audio control (Windows)
│   ├── monitoring.py     # Resource monitoring
│   └── network.py        # Wi‑Fi / clipboard
└── platform/
    └── telegram.py       # Telegram adapter
```

---

## 🧪 Testing

The test suite uses `pytest` and makes no real network / Telegram calls.

```bash
pip install -e .[dev]
pytest -v
```

Lint (matches CI, config lives in `.flake8`):

```bash
flake8 src tests
```

---

## 🔧 Installation extras

| Extra | Includes |
|---|---|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Everything above |
| `owlbot-remote[dev]` | Dev / CI tools (`build`, `flake8`, `pytest`) |

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

## 📚 Documentation

All guides and API references are in the [`docs/`](docs/) directory (English only):

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/GETTING_STARTED.md) | Installation, configuration, quick start |
| [Configuration](docs/CONFIGURATION.md) | Complete configuration reference |
| [Modules](docs/MODULES.md) | All modules, commands, and features |
| [API Reference](docs/API.md) | Python API reference |
| [Security](docs/SECURITY.md) | Security best practices |
| [Development](docs/DEVELOPMENT.md) | Contributing, testing, releasing |
| [Examples](docs/EXAMPLES.md) | Usage examples and patterns |
| [Documentation Index](docs/INDEX.md) | Full documentation index |

### 🌐 Translations (README only)

All technical docs are English-only. README translations are in [`docs/`](docs/):

| Language | File |
|----------|------|
| 🇮🇷 Persian/Farsi | [README-fa.md](docs/README-fa.md) |
| 🇪🇸 Spanish | [README-es.md](docs/README-es.md) |
| 🇮🇹 Italian | [README-it.md](docs/README-it.md) |
| 🇩🇪 German | [README-de.md](docs/README-de.md) |
| 🇨🇳 Chinese (Simplified) | [README-zh.md](docs/README-zh.md) |
| 🇫🇷 French | [README-fr.md](docs/README-fr.md) |
| 🇷🇺 Russian | [README-ru.md](docs/README-ru.md) |
| 🇯🇵 Japanese | [README-ja.md](docs/README-ja.md) |
| 🇳🇱 Dutch | [README-nl.md](docs/README-nl.md) |
| 🇹🇷 Turkish | [README-tr.md](docs/README-tr.md) |
| 🇰🇷 Korean | [README-ko.md](docs/README-ko.md) |

---

*Maintained by **Sepehr H.I** 🦉*
