# 📚 Examples & Tutorials

Practical examples for using OwlBot in various scenarios.

---

## 🚀 Quick Start Examples

### Minimal Bot (Cross-Platform)

```python
# minimal_bot.py
from owlbot import OwlBot

TOKEN = "YOUR_BOT_TOKEN"          # From @BotFather
USER_ID = 123456789               # Your Telegram user ID

bot = OwlBot(
    token=TOKEN,
    authorized_users=[USER_ID],
    modules=["system", "files"],  # Cross-platform only
)

if __name__ == "__main__":
    bot.run()
```

### Full Windows Bot (All Features)

```python
# full_windows_bot.py
from owlbot import OwlBot

TOKEN = "YOUR_BOT_TOKEN"
USER_ID = 123456789

bot = OwlBot(
    token=TOKEN,
    authorized_users=[USER_ID],
    modules=[
        "system", "screen", "files",
        "input", "processes", "monitoring",
        "audio", "network", "ffmpeg"
    ],
    log_level="INFO",
    log_file="owlbot.log",
)

if __name__ == "__main__":
    bot.run()
```

### Multiple Authorized Users

```python
# multi_user_bot.py
from owlbot import OwlBot

ADMIN_ID = 123456789
FAMILY_IDS = [987654321, 555666777]

bot = OwlBot(
    token="YOUR_TOKEN",
    authorized_users=[ADMIN_ID] + FAMILY_IDS,
    modules=["system", "screen", "files", "monitoring"],
)

# Admin-only commands can check user ID in custom handlers
@bot.on_command("admin_only")
def admin_only(ctx):
    if ctx.user_id != ADMIN_ID:
        ctx.reply("❌ Admin only!")
        return
    ctx.reply("✅ Admin command executed")

bot.run()
```

---

## ⚙️ Advanced Configuration

### Using BotConfig Directly

```python
# config_advanced.py
from owlbot import OwlBot
from owlbot.config import BotConfig

config = BotConfig(
    token="YOUR_TOKEN",
    authorized_users=[123456789],
    modules=["system", "screen", "files"],
    log_level="DEBUG",
    log_file="debug.log",
    enable_logging=True,
    
    # Audio settings
    audio_sample_rate=44100,
    audio_chunk_size=2048,
    max_record_duration=300,
    
    # File limits
    max_file_size_mb=100,
    max_download_mb=50,
    
    # Stream settings
    stream_fps=10,
    stream_jpeg_quality=70,
    
    # Monitoring
    monitor_interval=5,
    
    # Custom protected processes
    protected_processes=frozenset({
        "system", "svchost.exe", "my-critical-app.exe"
    }),
)

bot = OwlBot(config=config)
bot.run()
```

### Environment-Based Configuration

```python
# env_config.py
import os
from owlbot import OwlBot

bot = OwlBot(
    token=os.environ["OWLBOT_TOKEN"],
    authorized_users=[
        int(x) for x in os.environ["OWLBOT_USERS"].split(",")
    ],
    modules=os.environ.get("OWLBOT_MODULES", "system,screen,files").split(","),
    log_level=os.environ.get("OWLBOT_LOG_LEVEL", "INFO"),
    log_file=os.environ.get("OWLBOT_LOG_FILE", "owlbot.log"),
    enable_logging=os.environ.get("OWLBOT_ENABLE_LOGGING", "true").lower() != "false",
)

bot.run()
```

```bash
# .env file (use python-dotenv)
OWLBOT_TOKEN=123:ABC
OWLBOT_USERS=123456789,987654321
OWLBOT_MODULES=system,screen,files,monitoring
OWLBOT_LOG_LEVEL=DEBUG
OWLBOT_LOG_FILE=owlbot.log
OWLBOT_ENABLE_LOGGING=true
```

---

## 🔧 Custom Module Development

### Creating a Custom Module

```python
# my_modules/weather.py
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import authorized_only, safe_reply
import requests

class WeatherModule(BaseModule):
    name = "weather"
    description = "Weather information module"
    commands = {
        "weather": "Get current weather for a city",
        "forecast": "Get 3-day forecast",
    }
    
    def __init__(self, bot, config):
        super().__init__(bot, config)
        self.api_key = config.get("weather_api_key")
    
    @authorized_only
    @safe_reply
    def cmd_weather(self, ctx):
        """Usage: /weather <city>"""
        city = ctx.args.strip() or "Tehran"
        weather = self.get_weather(city)
        ctx.reply(f"🌤️ {city}: {weather}")
    
    @authorized_only
    @safe_reply
    def cmd_forecast(self, ctx):
        """Usage: /forecast <city>"""
        city = ctx.args.strip() or "Tehran"
        forecast = self.get_forecast(city)
        ctx.reply(f"📅 3-Day Forecast for {city}:\n{forecast}")
    
    def get_weather(self, city):
        # Your API call here
        return f"22°C, Sunny"
    
    def get_forecast(self, city):
        return "Day 1: 22°C\nDay 2: 20°C\nDay 3: 19°C"

# Register in your main bot
from owlbot import OwlBot

bot = OwlBot(token=TOKEN, authorized_users=[UID])
bot.register_module(WeatherModule)
bot.run()
```

### Module with Configuration

```python
# my_modules/reminder.py
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import authorized_only, safe_reply
from dataclasses import dataclass, field
from typing import Optional
import asyncio

@dataclass
class ReminderConfig:
    enabled: bool = True
    max_reminders: int = 10

class ReminderModule(BaseModule):
    name = "reminder"
    description = "Personal reminder system"
    config_class = ReminderConfig
    
    def __init__(self, bot, config):
        super().__init__(bot, config)
        self.reminders = []
        self.config = config  # Validated config instance
    
    @authorized_only
    @safe_reply
    def cmd_remind(self, ctx):
        """Usage: /remind <minutes> <message>"""
        parts = ctx.args.split(maxsplit=1)
        if len(parts) < 2:
            ctx.reply("Usage: /remind <minutes> <message>")
            return
        
        try:
            minutes = int(parts[0])
            message = parts[1]
        except ValueError:
            ctx.reply("Invalid minutes value")
            return
        
        if len(self.reminders) >= self.config.max_reminders:
            ctx.reply("Max reminders reached")
            return
        
        self.reminders.append({
            "user": ctx.user_id,
            "message": message,
            "time": minutes * 60
        })
        ctx.reply(f"⏰ Reminder set for {minutes} min: {message}")
        asyncio.create_task(self._trigger_reminder(len(self.reminders)-1))
    
    async def _trigger_reminder(self, index):
        await asyncio.sleep(self.reminders[index]["time"])
        reminder = self.reminders.pop(index)
        await self.bot.send_message(
            reminder["user"],
            f"⏰ Reminder: {reminder['message']}"
        )
```

---

## 🖥️ CLI Usage Examples

### Development / Testing

```bash
# Quick test with minimal modules
owlbot --token $TOKEN --users $UID --modules system,files --log-level DEBUG

# Test specific module
owlbot --token $TOKEN --users $UID --modules screen --log-level DEBUG

# Silent test (no log file)
owlbot --token $TOKEN --users $UID --no-log-file
```

### Production Deployment

```bash
# Full production with logging
owlbot \
  --token $OWLBOT_TOKEN \
  --users $OWLBOT_USERS \
  --modules system,screen,files,input,processes,monitoring,audio,network,ffmpeg \
  --log-level INFO \
  --log-file /var/log/owlbot/owlbot.log
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/owlbot.service
[Unit]
Description=OwlBot Telegram Remote Control
After=network.target

[Service]
Type=simple
User=owlbot
WorkingDirectory=/opt/owlbot
EnvironmentFile=/opt/owlbot/.env
ExecStart=/opt/owlbot/.venv/bin/owlbot
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable owlbot
sudo systemctl start owlbot
sudo journalctl -u owlbot -f
```

### Windows Service (NSSM)

```cmd
# Install NSSM
nssm install OwlBot
# Path: C:\Python311\python.exe
# Startup directory: C:\OwlBot
# Arguments: -m owlbot --token TOKEN --users 123
nssm set OwlBot AppStdout C:\OwlBot\owlbot.log
nssm set OwlBot AppStderr C:\OwlBot\owlbot_error.log
nssm start OwlBot
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for Windows modules (if using wine)
# RUN apt-get update && apt-get install -y ffmpeg

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir -e .[all]

ENV OWLBOT_TOKEN=""
ENV OWLBOT_USERS=""
ENV OWLBOT_MODULES="system,screen,files,monitoring"
ENV OWLBOT_LOG_LEVEL="INFO"

CMD ["owlbot"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  owlbot:
    build: .
    container_name: owlbot
    restart: unless-stopped
    environment:
      - OWLBOT_TOKEN=${OWLBOT_TOKEN}
      - OWLBOT_USERS=${OWLBOT_USERS}
      - OWLBOT_MODULES=system,screen,files,monitoring
      - OWLBOT_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    # For screen capture on Linux:
    # devices:
    #   - /dev/dri:/dev/dri
    # environment:
    #   - DISPLAY=:99
```

```bash
# .env
OWLBOT_TOKEN=123:ABC
OWLBOT_USERS=123456789

docker-compose up -d
docker-compose logs -f
```

---

## 🔐 Security Best Practices

### 1. Token Security

```python
# ❌ BAD - Hardcoded
TOKEN = "123:ABC"

# ✅ GOOD - Environment variable
import os
TOKEN = os.environ["OWLBOT_TOKEN"]

# ✅ GOOD - Config file (gitignored)
# config.yaml (add to .gitignore)
```

### 2. User Authorization

```python
# ✅ GOOD - Explicit allowlist
AUTHORIZED_USERS = [123456789, 987654321]  # Specific IDs only

# ❌ BAD - Allow all (if somehow possible)
# AUTHORIZED_USERS = []  # Would be rejected by validation
```

### 3. Command Restrictions

```python
# Admin-only commands
ADMIN_ID = 123456789

@bot.on_command("shutdown")
def shutdown(ctx):
    if ctx.user_id != ADMIN_ID:
        ctx.reply("❌ Admin only")
        return
    # ... shutdown logic
```

### 4. File Access Limits

```python
config = BotConfig(
    max_file_size_mb=50,      # Limit upload size
    max_download_mb=20,       # Limit download size
    # Protected processes can't be killed
    protected_processes=frozenset({
        "system", "svchost.exe", "critical-app.exe"
    }),
)
```

---

## 📱 Telegram Bot Setup

### 1. Create Bot

1. Open Telegram → Search `@BotFather`
2. Send `/newbot`
3. Choose name: `My OwlBot`
4. Choose username: `my_owlbot_bot`
5. Copy token: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Get Your User ID

1. Search `@userinfobot` in Telegram
2. Start bot → It replies with your ID
3. Or use `@RawDataBot` → Forward any message

### 3. Test Connection

```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
# Should return bot info JSON
```

---

## 🐛 Troubleshooting

### Bot Doesn't Start

```bash
# Check token format
owlbot --token "123:ABC" --users 123 --log-level DEBUG

# Common issues:
# - Token must be "NUMBER:STRING" format
# - User ID must be integer
# - No spaces in comma-separated lists
```

### Modules Not Loading

```bash
# Check missing dependencies
pip install owlbot-remote[ui]      # For screen module
pip install owlbot-remote[windows] # For Windows modules
pip install owlbot-remote[all]     # Everything
```

### Screen/Webcam Not Working (Linux)

```bash
# Install system dependencies
sudo apt-get install -y \
  python3-dev \
  libopencv-dev \
  libgtk-3-dev \
  libx11-dev \
  libxtst-dev \
  ffmpeg

# For headless servers, use virtual display:
# Xvfb :99 -screen 0 1920x1080x24 &
# export DISPLAY=:99
```

### Audio Not Working (Windows)

```bash
# Install Windows dependencies
pip install owlbot-remote[windows]

# Check audio devices in Windows Settings
# Ensure microphone access is allowed for Python
```

### Permission Errors

```bash
# Windows: Run as Administrator for some commands
# /shutdown, /restart, /killtask (system processes)

# Linux: Add user to necessary groups
sudo usermod -a -G video,input $USER
```

---

## 📖 Further Reading

- [Configuration Reference](CONFIGURATION.md)
- [Module Reference](MODULES.md)
- [API Reference](API.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)