# ⚙️ Configuration Reference

Complete reference for all OwlBot configuration options.

---

## 📋 BotConfig Class

```python
from owlbot.config import BotConfig

config = BotConfig(
    # Required
    token: str,
    authorized_users: List[int],
    
    # Platform
    platform: str = "telegram",
    
    # Modules
    modules: List[str] = AVAILABLE_MODULES,
    
    # Logging
    log_level: str = "INFO",
    log_file: Optional[str] = "owlbot.log",
    enable_logging: bool = True,
    
    # Audio
    audio_sample_rate: int = 16000,
    audio_chunk_size: int = 1024,
    audio_channels: int = 1,
    max_record_duration: int = 120,
    min_record_duration: int = 1,
    
    # File Transfer
    max_file_size_mb: int = 50,
    max_download_mb: int = 20,
    max_timelapse_count: int = 60,
    
    # Screen / Stream
    stream_fps: int = 5,
    screenshot_quality: int = 85,
    stream_jpeg_quality: int = 50,
    stream_frame_delay: float = 0.2,
    stream_photo_interval: float = 1.0,
    
    # Monitoring
    monitor_interval: int = 10,
    
    # Protected Processes
    protected_processes: FrozenSet[str] = DEFAULT_PROTECTED,
)
```

---

## 🔑 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `token` | `str` | Telegram Bot Token from @BotFather (format: `123:ABC`) |
| `authorized_users` | `List[int]` | List of Telegram User IDs allowed to control the bot |

```python
# Minimal valid config
config = BotConfig(
    token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    authorized_users=[123456789],
)
```

---

## 🌐 Platform & Modules

### `platform`
- **Type**: `str`
- **Default**: `"telegram"`
- **Description**: Bot platform adapter. Currently only `"telegram"` is supported.

### `modules`
- **Type**: `List[str]`
- **Default**: All available modules for current platform
- **Valid values**: `"system"`, `"screen"`, `"audio"`, `"files"`, `"input"`, `"processes"`, `"monitoring"`, `"network"`, `"ffmpeg"`
- **Platform restrictions**:
  - `audio`, `input`, `network`, `ffmpeg`: Windows only

```python
# Cross-platform only
config = BotConfig(..., modules=["system", "files", "processes", "monitoring"])

# Full Windows
config = BotConfig(
    ...,
    modules=[
        "system", "screen", "audio", "files",
        "input", "processes", "monitoring",
        "network", "ffmpeg"
    ]
)
```

---

## 📝 Logging Configuration

### `log_level`
- **Type**: `str`
- **Default**: `"INFO"`
- **Valid**: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`

### `log_file`
- **Type**: `Optional[str]`
- **Default**: `"owlbot.log"`
- **Behavior**: 
  - `None` or `""` → No log file (console only)
  - Path string → Rotating file handler at that path

### `enable_logging`
- **Type**: `bool`
- **Default**: `True`
- **Behavior**: 
  - `True` → Full logging (console + file per `log_file`)
  - `False` → Completely disabled (no handlers at all)

| Goal | `log_file` | `enable_logging` |
|------|------------|------------------|
| Console + file (default) | `"owlbot.log"` | `True` |
| Console only, no file | `None` or `""` | `True` |
| Completely silent | any | `False` |

```python
# Console only
BotConfig(..., log_file=None, enable_logging=True)

# Silent
BotConfig(..., enable_logging=False)

# Custom log file
BotConfig(..., log_file="/var/log/owlbot/bot.log")
```

---

## 🔊 Audio Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `audio_sample_rate` | `int` | `16000` | 8000–48000 | Sample rate for recording |
| `audio_chunk_size` | `int` | `1024` | 256–8192 | Buffer chunk size |
| `audio_channels` | `int` | `1` | 1 or 2 | Mono/stereo |
| `max_record_duration` | `int` | `120` | 1–3600 | Max recording seconds |
| `min_record_duration` | `int` | `1` | 1–60 | Min recording seconds |

```python
BotConfig(
    ...,
    audio_sample_rate=44100,      # CD quality
    audio_chunk_size=2048,        # Lower latency
    audio_channels=2,             # Stereo
    max_record_duration=300,      # 5 minutes
)
```

---

## 📁 File Transfer Limits

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_file_size_mb` | `int` | `50` | Max file size bot can send |
| `max_download_mb` | `int` | `20` | Max file size bot can download |
| `max_timelapse_count` | `int` | `60` | Max screenshots in timelapse |

```python
BotConfig(
    ...,
    max_file_size_mb=100,   # Allow larger files
    max_download_mb=50,
    max_timelapse_count=120,
)
```

---

## 📸 Screen & Stream Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `stream_fps` | `int` | `5` | 1–30 | Stream frames per second |
| `screenshot_quality` | `int` | `85` | 1–100 | JPEG quality for screenshots |
| `stream_jpeg_quality` | `int` | `50` | 1–100 | JPEG quality for stream frames |
| `stream_frame_delay` | `float` | `0.2` | 0.05–2.0 | Delay between stream frames |
| `stream_photo_interval` | `float` | `1.0` | 0.1–10.0 | Interval for `/startstream` photo mode |

```python
BotConfig(
    ...,
    stream_fps=15,              # Smoother stream
    screenshot_quality=95,      # High quality screenshots
    stream_jpeg_quality=70,     # Better stream quality
    stream_frame_delay=0.1,     # Faster frame rate
)
```

---

## 📊 Monitoring Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `monitor_interval` | `int` | `10` | Seconds between monitoring checks |

```python
BotConfig(
    ...,
    monitor_interval=5,  # Check every 5 seconds
)
```

---

## 🛡️ Protected Processes

### `protected_processes`
- **Type**: `FrozenSet[str]`
- **Default**: System-critical Windows processes
- **Description**: Processes that cannot be killed via `/killtask`

```python
from owlbot.config import BotConfig

config = BotConfig(
    ...,
    protected_processes=frozenset({
        "system", "svchost.exe", "csrss.exe", "winlogon.exe",
        "lsass.exe", "services.exe", "smss.exe", "wininit.exe",
        "dwm.exe", "ntoskrnl.exe",
        "my-critical-app.exe",  # Add your own
    }),
)
```

**Default protected processes:**
- `system` — Kernel
- `svchost.exe` — Service host
- `csrss.exe` — Client/Server Runtime
- `winlogon.exe` — Windows Logon
- `lsass.exe` — Local Security Authority
- `services.exe` — Service Control Manager
- `smss.exe` — Session Manager
- `wininit.exe` — Windows Init
- `dwm.exe` — Desktop Window Manager
- `ntoskrnl.exe` — NT Kernel

---

## 📦 Available Module Constants

```python
from owlbot.config import (
    AVAILABLE_MODULES,
    WINDOWS_ONLY_MODULES,
    CROSS_PLATFORM_MODULES,
    VALID_LOG_LEVELS,
)

# All modules
AVAILABLE_MODULES = frozenset({
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring",
    "network", "ffmpeg"
})

# Windows-only
WINDOWS_ONLY_MODULES = frozenset({"audio", "input"})

# Cross-platform
CROSS_PLATFORM_MODULES = AVAILABLE_MODULES - WINDOWS_ONLY_MODULES

# Valid log levels
VALID_LOG_LEVELS = frozenset({
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
})
```

---

## 🔧 CLI Arguments Mapping

| CLI Argument | Config Field | Type |
|--------------|--------------|------|
| `--token` | `token` | `str` |
| `--users` | `authorized_users` | `List[int]` |
| `--modules` | `modules` | `List[str]` |
| `--log-level` | `log_level` | `str` |
| `--log-file` | `log_file` | `str` |
| `--no-log-file` | `log_file=None` | `flag` |
| `--disable-logging` | `enable_logging=False` | `flag` |

```bash
# Equivalent configurations:
owlbot --token TOKEN --users 123,456 --modules system,screen \
       --log-level DEBUG --log-file bot.log

# Python
BotConfig(
    token="TOKEN",
    authorized_users=[123, 456],
    modules=["system", "screen"],
    log_level="DEBUG",
    log_file="bot.log",
)
```

---

## 🌍 Environment Variables

| Variable | Config Field | Example |
|----------|--------------|---------|
| `OWLBOT_TOKEN` | `token` | `123:ABC` |
| `OWLBOT_USERS` | `authorized_users` | `123,456,789` |
| `OWLBOT_MODULES` | `modules` | `system,screen,files` |
| `OWLBOT_LOG_LEVEL` | `log_level` | `DEBUG` |
| `OWLBOT_LOG_FILE` | `log_file` | `/var/log/owlbot.log` |
| `OWLBOT_ENABLE_LOGGING` | `enable_logging` | `true`/`false` |

```python
import os

config = BotConfig(
    token=os.environ["OWLBOT_TOKEN"],
    authorized_users=[int(x) for x in os.environ["OWLBOT_USERS"].split(",")],
    modules=os.environ.get("OWLBOT_MODULES", "system,screen,files").split(","),
    log_level=os.environ.get("OWLBOT_LOG_LEVEL", "INFO"),
    log_file=os.environ.get("OWLBOT_LOG_FILE", "owlbot.log"),
    enable_logging=os.environ.get("OWLBOT_ENABLE_LOGGING", "true").lower() != "false",
)
```

---

## ✅ Validation Rules

| Field | Validation |
|-------|------------|
| `token` | Non-empty string |
| `authorized_users` | Non-empty list of positive integers |
| `modules` | Subset of `AVAILABLE_MODULES` |
| `log_level` | In `VALID_LOG_LEVELS` (case-insensitive) |
| `log_file` | `None`/`""` or valid path string |
| `audio_sample_rate` | 8000–48000 |
| `audio_chunk_size` | Power of 2, 256–8192 |
| `audio_channels` | 1 or 2 |
| `max_record_duration` | 1–3600 |
| `stream_fps` | 1–30 |
| `*_quality` | 1–100 |
| `monitor_interval` | 1–3600 |

Validation happens in `__post_init__` — invalid config raises `ValueError` immediately.

---

## 📝 Complete Example

```python
from owlbot import OwlBot
from owlbot.config import BotConfig

config = BotConfig(
    # Required
    token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    authorized_users=[123456789, 987654321],
    
    # Modules (Windows full)
    modules=[
        "system", "screen", "audio", "files",
        "input", "processes", "monitoring",
        "network", "ffmpeg"
    ],
    
    # Logging
    log_level="DEBUG",
    log_file="logs/owlbot.log",
    enable_logging=True,
    
    # Audio
    audio_sample_rate=44100,
    audio_chunk_size=2048,
    audio_channels=2,
    max_record_duration=300,
    
    # Files
    max_file_size_mb=100,
    max_download_mb=50,
    
    # Stream
    stream_fps=10,
    screenshot_quality=90,
    stream_jpeg_quality=60,
    
    # Monitoring
    monitor_interval=5,
    
    # Security
    protected_processes=frozenset({
        "system", "svchost.exe", "critical-app.exe"
    }),
)

bot = OwlBot(config=config)
bot.run()
```