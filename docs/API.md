# 📚 API Reference

Complete Python API reference for OwlBot.

---

## 📦 Package Exports

```python
from owlbot import OwlBot, BotConfig
from owlbot.config import (
    AVAILABLE_MODULES,
    WINDOWS_ONLY_MODULES,
    CROSS_PLATFORM_MODULES,
    VALID_LOG_LEVELS,
)
```

---

## 🦉 OwlBot Class

Main bot engine class.

### Constructor

```python
class OwlBot:
    def __init__(
        self,
        token: str,
        authorized_users: list[int],
        *,
        modules: list[str] | None = None,
        log_level: str = "INFO",
        log_file: str | None = "owlbot.log",
        enable_logging: bool = True,
        config: BotConfig | None = None,
    ) -> None:
        """
        Initialize OwlBot.
        
        Parameters
        ----------
        token : str
            Telegram Bot Token from @BotFather
        authorized_users : list[int]
            List of authorized Telegram user IDs
        modules : list[str], optional
            Modules to load (default: all available for platform)
        log_level : str, default "INFO"
            Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        log_file : str or None, default "owlbot.log"
            Log file path (None/empty = no file)
        enable_logging : bool, default True
            Master logging switch
        config : BotConfig, optional
            Advanced config object (overrides other params)
        """
```

### Methods

#### `run()`

```python
def run(self) -> None:
    """
    Start the bot and block until stopped.
    
    This method:
    - Initializes all modules
    - Connects to Telegram
    - Starts polling loop
    - Handles graceful shutdown on SIGINT/SIGTERM
    
    Raises
    ------
    RuntimeError
        If bot is already running
    ConnectionError
        If Telegram connection fails
    """
```

#### `stop()`

```python
def stop(self) -> None:
    """
    Stop the bot gracefully.
    
    - Stops polling
    - Cleans up modules
    - Closes logging handlers
    """
```

#### `send_message()`

```python
async def send_message(
    self,
    user_id: int,
    text: str,
    parse_mode: str = "Markdown",
    **kwargs
) -> Message:
    """
    Send a message to a user.
    
    Parameters
    ----------
    user_id : int
        Telegram user ID
    text : str
        Message text
    parse_mode : str, default "Markdown"
        "Markdown", "HTML", or None
    **kwargs
        Additional Telegram API parameters
    
    Returns
    -------
    Message
        Sent message object
    """
```

#### `send_photo()`, `send_document()`, `send_video()`

```python
async def send_photo(self, user_id: int, photo: bytes | str, caption: str = "", **kwargs) -> Message:
    """Send photo to user. photo can be bytes or file path."""

async def send_document(self, user_id: int, document: bytes | str, filename: str = "", **kwargs) -> Message:
    """Send document/file to user."""

async def send_video(self, user_id: int, video: bytes | str, caption: str = "", **kwargs) -> Message:
    """Send video to user."""
```

#### `register_module()`

```python
def register_module(self, module_class: type[BaseModule]) -> None:
    """
    Register a custom module class.
    
    Parameters
    ----------
    module_class : type[BaseModule]
        Module class to register (not instance)
    
    Example
    -------
    class MyModule(BaseModule):
        name = "custom"
        commands = {"hello": "Say hello"}
        
        def cmd_hello(self, ctx):
            ctx.reply("Hello!")
    
    bot.register_module(MyModule)
    """
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `loaded_modules` | `list[str]` | Names of currently loaded modules |
| `config` | `BotConfig` | Current configuration |
| `is_running` | `bool` | Whether bot is running |
| `start_time` | `float` | Process start timestamp |

---

## ⚙️ BotConfig Class

```python
from owlbot.config import BotConfig

@dataclass
class BotConfig:
    # Required
    token: str
    authorized_users: list[int]
    
    # Platform
    platform: str = "telegram"
    
    # Modules
    modules: list[str] = field(default_factory=lambda: list(AVAILABLE_MODULES))
    
    # Logging
    log_level: str = "INFO"
    log_file: str | None = "owlbot.log"
    enable_logging: bool = True
    
    # Audio
    audio_sample_rate: int = 16000
    audio_chunk_size: int = 1024
    audio_channels: int = 1
    max_record_duration: int = 120
    min_record_duration: int = 1
    
    # File Transfer
    max_file_size_mb: int = 50
    max_download_mb: int = 20
    max_timelapse_count: int = 60
    
    # Screen / Stream
    stream_fps: int = 5
    screenshot_quality: int = 85
    stream_jpeg_quality: int = 50
    stream_frame_delay: float = 0.2
    stream_photo_interval: float = 1.0
    
    # Monitoring
    monitor_interval: int = 10
    
    # Protected Processes
    protected_processes: frozenset[str] = field(default_factory=DEFAULT_PROTECTED)
    
    def __post_init__(self) -> None:
        """Validate all fields. Raises ValueError on invalid config."""
```

### Constants

```python
from owlbot.config import (
    AVAILABLE_MODULES,      # frozenset of all module names
    WINDOWS_ONLY_MODULES,   # frozenset({"audio", "input"})
    CROSS_PLATFORM_MODULES, # AVAILABLE_MODULES - WINDOWS_ONLY_MODULES
    VALID_LOG_LEVELS,       # frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
)
```

---

## 🧩 BaseModule Class

Base class for all modules.

```python
from owlbot.modules.base import BaseModule

class BaseModule:
    name: str                    # Module name (required)
    description: str = ""        # Module description
    commands: dict[str, str] = {} # Command -> description mapping
    
    def __init__(self, bot: "OwlBot", config: BotConfig) -> None:
        """
        Initialize module.
        
        Parameters
        ----------
        bot : OwlBot
            Parent bot instance
        config : BotConfig
            Bot configuration
        """
    
    async def on_load(self) -> None:
        """Called when module is loaded. Override for setup."""
    
    async def on_unload(self) -> None:
        """Called when module is unloaded. Override for cleanup."""
    
    def get_help(self) -> str:
        """Return help text for this module."""
```

### Command Methods

Commands are auto-discovered from methods named `cmd_<name>`:

```python
class MyModule(BaseModule):
    name = "example"
    commands = {
        "hello": "Say hello",
        "echo": "Echo back text",
    }
    
    @authorized_only  # Decorator for auth check
    @safe_reply       # Decorator for error handling
    def cmd_hello(self, ctx: CommandContext) -> None:
        """Usage: /hello"""
        ctx.reply("Hello! 👋")
    
    @authorized_only
    @safe_reply
    def cmd_echo(self, ctx: CommandContext) -> None:
        """Usage: /echo <text>"""
        ctx.reply(ctx.args or "Nothing to echo")
```

---

## 🎯 CommandContext Class

Context passed to command handlers.

```python
from owlbot.core.decorators import CommandContext

class CommandContext:
    # Message info
    message: Message           # Original Telegram message
    user_id: int               # Sender user ID
    chat_id: int               # Chat ID
    text: str                  # Full message text
    command: str               # Command name (without /)
    args: str                  # Arguments after command
    
    # Bot reference
    bot: OwlBot                # Parent bot instance
    config: BotConfig          # Bot configuration
    
    # Reply methods
    def reply(self, text: str, parse_mode: str = "Markdown", **kwargs) -> Message:
        """Quick reply to the command."""
    
    def reply_photo(self, photo: bytes | str, caption: str = "", **kwargs) -> Message:
        """Reply with photo."""
    
    def reply_document(self, document: bytes | str, filename: str = "", **kwargs) -> Message:
        """Reply with document."""
    
    # Authorization
    def is_authorized(self) -> bool:
        """Check if user is authorized."""
    
    def require_auth(self) -> bool:
        """Check auth, send error if not authorized. Returns True if authorized."""
```

---

## 🛡️ Decorators

### `@authorized_only`

```python
from owlbot.core.decorators import authorized_only

@authorized_only
def cmd_secret(self, ctx):
    """Only authorized users can use this."""
    ctx.reply("Secret info!")
```

### `@safe_reply`

```python
from owlbot.core.decorators import safe_reply

@safe_reply
def cmd_risky(self, ctx):
    """Exceptions are caught and user gets error message."""
    result = risky_operation()
    ctx.reply(f"Result: {result}")
```

### `@admin_only`

```python
from owlbot.core.decorators import admin_only

ADMIN_ID = 123456789

@admin_only(ADMIN_ID)
def cmd_shutdown(self, ctx):
    """Only admin can shutdown."""
    ctx.bot.stop()
```

---

## 🔧 Utility Functions

```python
from owlbot.core.utils import (
    format_bytes,
    format_duration,
    format_percent,
    get_system_info,
    run_command,
    run_python_script,
    is_windows,
    is_admin,
)

# Format helpers
format_bytes(1024**3)        # "1.0 GB"
format_duration(3661)        # "1h 1m 1s"
format_percent(0.42)         # "42%"

# System
get_system_info()            # Dict with CPU, RAM, disk, etc.
is_windows()                 # True on Windows
is_admin()                   # True if running as admin

# Execution
run_command("dir")           # (stdout, stderr, returncode)
run_python_script("print(1+1)")  # (stdout, stderr, returncode)
```

---

## 📋 Module Interfaces

### SystemModule

```python
from owlbot.modules.system import SystemModule

# Commands: /status, /uptime, /ping, /lock, /shutdown, /restart
```

### ScreenModule

```python
from owlbot.modules.screen import ScreenModule

# Commands: /screenshot, /webcam, /timelapse, /startstream, /stopstream
# Methods:
# - capture_screenshot() -> bytes
# - capture_webcam() -> bytes
# - start_timelapse(interval, count) -> list[bytes]
# - start_stream(fps, quality) -> async generator
```

### FilesModule

```python
from owlbot.modules.files import FilesModule

# Commands: /listdir, /getfile, /download, /hide, /show, /file
# Methods:
# - list_dir(path) -> list[FileInfo]
# - get_file(path) -> bytes
# - download_url(url, dest) -> str
# - file_op(op, src, dst) -> bool
```

### InputModule (Windows)

```python
from owlbot.modules.input import InputModule

# Commands: /type, /move, /mousepos, /mouse, /hotkey, /msg
# Methods:
# - type_text(text) -> None
# - move_mouse(x, y) -> None
# - mouse_action(action, **kwargs) -> None
# - send_hotkey(keys) -> None
# - show_message(text, title) -> int
```

### ProcessesModule

```python
from owlbot.modules.processes import ProcessesModule

# Commands: /tasklist, /killtask, /run, /cmd, /script, /runscript
# Methods:
# - list_processes(limit=20) -> list[ProcessInfo]
# - kill_process(name) -> int  # returns killed count
# - run_program(cmd) -> (stdout, stderr, code)
# - run_shell(cmd) -> (stdout, stderr, code)
# - run_python(code) -> (stdout, stderr, code)
# - run_script(path) -> (stdout, stderr, code)
```

### MonitoringModule

```python
from owlbot.modules.monitoring import MonitoringModule

# Commands: /monitor, /stopmonitor
# Methods:
# - start_monitor(type) -> None  # cpu, ram, disk, temp, all
# - stop_monitor() -> None
# - get_current_stats() -> dict
```

### AudioModule (Windows)

```python
from owlbot.modules.audio import AudioModule

# Commands: /mute, /unmute, /volume, /startrec, /stoprec, /playvoice
# Methods:
# - set_mute(mute) -> None
# - set_volume(level) -> None  # 0-100
# - get_volume() -> int
# - start_recording(duration) -> None
# - stop_recording() -> bytes
# - toggle_voice_playback() -> bool
```

### NetworkModule (Windows)

```python
from owlbot.modules.network import NetworkModule

# Commands: /netcheck, /wifiscan, /clipboard
# Methods:
# - check_internet() -> bool
# - scan_wifi() -> list[WifiInfo]
# - get_clipboard() -> str
# - set_clipboard(text) -> None
```

### FFmpegModule (Windows)

```python
from owlbot.modules.ffmpeg import FFmpegModule

# Commands: /ffmpeg, /ffmpeg_install
# Methods:
# - check_ffmpeg() -> bool
# - install_ffmpeg() -> bool
# - get_ffmpeg_path() -> str | None
```

---

## 📊 Type Definitions

```python
from owlbot.config import BotConfig
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import CommandContext

# Main types
OwlBotType = "OwlBot"
ModuleType = type[BaseModule]
ContextType = CommandContext

# Config types
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ModuleName = Literal[
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring",
    "network", "ffmpeg"
]
```

---

## 🔌 Extension Points

### Custom Command Handler

```python
from owlbot import OwlBot
from owlbot.core.decorators import authorized_only, safe_reply

bot = OwlBot(token=TOKEN, authorized_users=[UID])

# Register ad-hoc command
@bot.on_command("custom")
@authorized_only
@safe_reply
def custom_command(ctx):
    ctx.reply("Custom command executed!")

# Or with full control
@bot.on_message()
def handle_all_messages(ctx):
    if ctx.text.startswith("!"):
        ctx.reply(f"You said: {ctx.text}")

bot.run()
```

### Event Hooks

```python
# Before/after command execution
@bot.before_command
def before_cmd(ctx):
    print(f"Executing: {ctx.command}")

@bot.after_command
def after_cmd(ctx, result):
    print(f"Completed: {ctx.command}")

# Error handler
@bot.on_error
def handle_error(ctx, error):
    print(f"Error in {ctx.command}: {error}")
    # Don't reply here - safe_reply handles it
```

---

## 📝 Complete Usage Example

```python
#!/usr/bin/env python3
"""
Full-featured OwlBot example with custom module and event hooks.
"""
import os
from owlbot import OwlBot
from owlbot.config import BotConfig
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import authorized_only, safe_reply

# 1. Configuration
config = BotConfig(
    token=os.environ["OWLBOT_TOKEN"],
    authorized_users=[int(x) for x in os.environ["OWLBOT_USERS"].split(",")],
    modules=["system", "screen", "files", "monitoring"],
    log_level="INFO",
    log_file="owlbot.log",
)

# 2. Create bot
bot = OwlBot(config=config)

# 3. Custom module
class TimeModule(BaseModule):
    name = "time"
    description = "Time and date utilities"
    commands = {
        "time": "Show current time",
        "date": "Show current date",
        "timezone": "Show timezone info",
    }
    
    @authorized_only
    @safe_reply
    def cmd_time(self, ctx):
        from datetime import datetime
        ctx.reply(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    @authorized_only
    @safe_reply
    def cmd_date(self, ctx):
        from datetime import datetime
        ctx.reply(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
    
    @authorized_only
    @safe_reply
    def cmd_timezone(self, ctx):
        import time
        ctx.reply(f"🌍 Timezone: {time.tzname[0]} (UTC{time.timezone//3600:+d})")

# 4. Register custom module
bot.register_module(TimeModule)

# 5. Event hooks
@bot.before_command
def log_command(ctx):
    print(f"[{ctx.user_id}] /{ctx.command} {ctx.args}")

@bot.on_error
def log_error(ctx, error):
    print(f"ERROR in /{ctx.command}: {error}")

# 6. Run
if __name__ == "__main__":
    print("Starting OwlBot...")
    bot.run()
```