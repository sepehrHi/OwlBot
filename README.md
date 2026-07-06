
# 🦉 OwlBot (owlbot-remote)

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Operating System](https://img.shields.io/badge/OS-Windows-1f92e2.svg)](https://www.microsoft.com/windows)
[![Stage](https://img.shields.io/badge/Release-1.0.0--beta-orange.svg)]()

**OwlBot** is a professional, production-ready, modular Windows remote management framework. It allows power users, developers, and system administrators to securely control, monitor, and interact with their Windows workstations remotely through chat platforms like Telegram.

Built with a modern **decoupled architecture**, OwlBot separates core OS control from the communication platform using **Dependency Injection**, making it incredibly lightweight, robust, and future-proof.

---

## ✨ Features

- 🧩 **100% Modular Design:** Load only the components you need (`system`, `audio`, `monitoring`, etc.) via a simple configuration list.
- 💉 **Dependency Injection:** Fully isolated core engine, prepared for multi-platform support (Telegram, Discord, SSH, etc.).
- 🛡️ **Built-in Security:** Access restriction out-of-the-box via explicit user ID white-listing.
- 🩹 **Fault-Tolerant Engine:** Centralized error handling using `@safe_reply` decorators ensures the bot never crashes on runtime unexpected OS errors.
- 📊 **Resource Monitoring:** Live tracking of CPU, RAM, Disk usage, and hardware temperatures.
- 🎹 **Peripherals Control:** Full remote typing, mouse moving/clicking, hotkey execution, and system audio manipulation.

---

## 🚀 Quick Start

### 1. Prerequisites
OwlBot requires **Python 3.11 or higher** running on a **Windows** machine. Some audio modules also require `ffmpeg` installed in your system PATH for voice playback conversions.

### 2. Private Installation Guide
Since this framework is distributed as a standalone private build, you can install it using one of the following methods instead of the public PyPI repository:

#### Method A: Via Local Wheel (.whl) File
Download the pre-compiled `.whl` package from your release channel and install it directly:
```bash
pip install ./owlbot_remote-1.0.0_beta-py3-none-any.whl

```

#### Method B: Directly From Private Git Repository

If you have access credentials to the source repository, install it via SSH or HTTPS target URLs:

```bash
git clone https://github.com/sepehrHi/OwlBot.git

```

#### Method C: Editable Mode (For Developers)

Navigate to the root folder containing `pyproject.toml` and trigger a local link build:

```bash
pip install -e .

```

### 3. Production Deployment Script

Create an execution script (e.g., `run_agent.py`) to fire up the module:

```python
from owlbot import OwlBot

# Initialize the core management engine
bot = OwlBot(
    token="YOUR_BOT_TOKEN",
    authorized_users=[7179034425],
    platform="telegram",
    modules=["system", "screen", "audio", "files", "input", "processes", "monitoring"],
    log_level="INFO",
    max_file_size_mb=50,
    screenshot_quality=85
)

if __name__ == "__main__":
    bot.run()

```

---

## 🕹️ Available Control Modules & Commands

| Module | Command | Description |
| --- | --- | --- |
| **`system`** | `/status` | View high-level metrics (CPU, RAM, Disk, Network, Battery). |
|  | `/uptime` | Get current machine uptime counter. |
|  | `/ping` | Health-check to verify agent responsiveness. |
|  | `/lock` | Instantly lock the Windows workstation. |
|  | `/shutdown` | Gracefully shut down the PC with a 3-second delay. |
|  | `/restart` | Gracefully restart the PC with a 3-second delay. |
| **`screen`** | `/screenshot` | Capture current high-res display layout. |
|  | `/webcam` | Take a quick photo using the default connected webcam. |
|  | `/timelapse <s> <n>` | Capture `n` screenshots sequentially every `s` seconds. |
|  | `/startstream` | Spawn a background thread to live-stream desktop movement. |
|  | `/stopstream` | Kill the active live-stream and compress it into a video file. |
| **`input`** | `/type <text>` | Perform native keystrokes to write out a string payload. |
|  | `/move <x> <y>` | Move the cursor smoothly to absolute coordinates. |
|  | `/mousepos` | Retrieve current pixel coordinate position of the cursor. |
|  | `/mouse <action>` | Perform mouse actions (`click left/right`, `scroll`, `drag`). |
|  | `/hotkey <k1+k2>` | Trigger custom global shortcut binds (e.g., `ctrl+c`). |
|  | `/msg <text>` | Pop up a native Windows Win32 Message Box window. |
| **`audio`** | `/mute` / `/unmute` | Toggle global master audio playback device mute states. |
|  | `/volume <0-100>` | Set master session volume matrix percentages dynamically. |
|  | `/startrec [sec]` | Initialize microphone capture worker (Default: 5s, Max: 120s). |
|  | `/stoprec` | Interrupt active voice recording and dispatch output WAV. |
|  | `/playvoice` | Toggle direct incoming user telegram voice-playback mode. |
| **`files`** | `/listdir [path]` | Explore and list full contents of specified windows directory. |
|  | `/getfile <path>` | Securely transfer a local asset file directly to chat channel. |
| **`processes`** | `/tasklist` | Print a clean text inventory of all active processes. |
|  | `/killtask <exe>` | Instantly kill an app (blocks system protected processes). |
| **`monitoring`** | `/monitor <mode>` | Activate scheduled polling warnings for `cpu`, `ram`, `disk`. |

---

## 📂 Architecture Structure

OwlBot follows strict clean coding layouts to keep development scalable:

```text
owlbot/
├── __init__.py           # Package exposures & version control
├── config.py             # Data-class schema models containing safety thresholds
├── core/
│   ├── bot.py            # Primary Engine lifecycle orchestrator
│   ├── decorators.py     # Resilient operational boundary controllers
│   └── utils.py          # Decoupled string and file manipulation units
├── modules/
│   ├── base.py           # Interface contracts for subsystem workers
│   └── system.py         # Concrete Windows core execution module
└── platforms/
    ├── base.py           # Unified interface for multiple bot services
    └── telegram.py       # Custom layer wrapper over pyTelegramBotAPI

```

---

## 🛠️ Contribution & Development

Want to add new platforms (like Discord or Slack) or custom modules?

1. Fork the repository.
2. Extend the `BaseModule` or `BasePlatform` abstract classes.
3. Inject your sub-component using the registry pattern located inside `owlbot/core/bot.py`.
4. Submit a Pull Request!

---

## 📄 License

Distributed under the **MIT License**. See the `LICENSE` file for more developer rights parameters.

Developed and maintained with precision by **MR_owl** 🦉

---
### 🌐 Open Source & Code Integrity Assurance

**OwlBot** is developed and distributed as an **open-source project** under the official parameters of the **MIT License**. 

* **Complete Data Sovereignty:** This agent is designed with a strict zero-telemetry architectural principle. The source code interacts exclusively with your local Windows operating system layer and your self-hosted chat infrastructure client. 
* **Zero Cloud Exposure:** No execution logs, runtime memory matrices, configuration variables, or environment tokens are cached, indexed, or shared with third-party cloud analytics databases. 
* **Local Compilation:** Because the compilation pipeline is executed strictly within your isolated local space (`.whl` building via local setuptools tools), you retain absolute control over your private binary assets and proprietary deployments.

*Maintained securely, transparently, and with full architectural privacy by **MR_owl**.* 🦉
