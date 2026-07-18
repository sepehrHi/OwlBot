# 🔒 Security Guide

Security best practices for deploying and running OwlBot safely.

---

## 🛡️ Core Security Principles

1. **Least Privilege** — Run with minimal required permissions
2. **Secret Management** — Never hardcode tokens or credentials
3. **Access Control** — Strict user authorization
4. **Audit Logging** — Monitor all bot activity
5. **Network Security** — Secure communication channels

---

## 🔐 Token Management

### ❌ Never Do This

```python
# BAD - Hardcoded token in source
bot = OwlBot(token="123456:ABC-DEF...", authorized_users=[123])

# BAD - Token in config file committed to git
# config.py
TOKEN = "123456:ABC-DEF..."
```

### ✅ Do This Instead

**Environment Variables (Recommended)**
```bash
# .env file (add to .gitignore!)
OWLBOT_TOKEN=123456:ABC-DEF...
OWLBOT_USERS=123456789,987654321
```

```python
import os
from owlbot import OwlBot

bot = OwlBot(
    token=os.environ["OWLBOT_TOKEN"],
    authorized_users=[int(x) for x in os.environ["OWLBOT_USERS"].split(",")],
)
```

**System Keyring (Windows)**
```python
import keyring

token = keyring.get_password("owlbot", "telegram_token")
bot = OwlBot(token=token, authorized_users=[...])
```

**Docker Secrets**
```yaml
# docker-compose.yml
services:
  owlbot:
    image: owlbot-remote
    secrets:
      - owlbot_token
    environment:
      - OWLBOT_TOKEN_FILE=/run/secrets/owlbot_token

secrets:
  owlbot_token:
    file: ./secrets/owlbot_token.txt
```

---

## 👥 User Authorization

### Authorized Users Only

```python
# ONLY these user IDs can control the bot
AUTHORIZED_USERS = [
    123456789,   # Your primary account
    987654321,   # Backup account
]

bot = OwlBot(token=TOKEN, authorized_users=AUTHORIZED_USERS)
```

### Finding Your User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Or use [@getmyid_bot](https://t.me/getmyid_bot)
3. Copy the numeric ID (e.g., `123456789`)

### Multi-User Setup

```python
# Family/team setup
AUTHORIZED_USERS = {
    "alice": 111111111,
    "bob": 222222222,
    "charlie": 333333333,
}

# In command handlers, check identity:
@authorized_only
def cmd_sensitive(ctx):
    user_name = next((k for k, v in AUTHORIZED_USERS.items() if v == ctx.user_id), "unknown")
    ctx.reply(f"Hello {user_name}!")
```

---

## 🚫 Command Restrictions

### Dangerous Commands (Require Extra Caution)

| Command | Risk | Mitigation |
|---------|------|------------|
| `/shutdown` | System shutdown | Confirmation prompt |
| `/restart` | System restart | Confirmation prompt |
| `/killtask` | Process termination | Protected process list |
| `/cmd` | Arbitrary shell execution | Admin-only, audit log |
| `/script` | Arbitrary Python execution | Admin-only, audit log |
| `/runscript` | Execute Python files | Admin-only, path validation |

### Protected Processes (Cannot Be Killed)

```python
from owlbot.config import BotConfig

config = BotConfig(
    ...,
    protected_processes=frozenset({
        "system", "svchost.exe", "csrss.exe", "winlogon.exe",
        "lsass.exe", "services.exe", "smss.exe", "wininit.exe",
        "dwm.exe", "ntoskrnl.exe",
        "antivirus.exe", "edr-agent.exe",  # Add your security tools
    }),
)
```

### Admin-Only Commands

```python
from owlbot.core.decorators import admin_only

ADMIN_ID = 123456789  # Only this user

@admin_only(ADMIN_ID)
def cmd_dangerous(ctx):
    """Only admin can execute."""
    ctx.bot.stop()
```

---

## 📁 File System Security

### Path Traversal Protection

```python
# Built-in: FilesModule validates paths
# - Resolves to absolute path
# - Checks against allowed roots
# - Blocks .. traversal attempts
```

### Safe Download Directory

```python
import tempfile
from pathlib import Path

# Use dedicated download directory
DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "owlbot_downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True, mode=0o700)

config = BotConfig(
    ...,
    # FilesModule uses this internally
)
```

### File Size Limits

```python
BotConfig(
    ...,
    max_file_size_mb=50,      # Max file bot can send
    max_download_mb=20,       # Max URL download size
    max_timelapse_count=60,   # Max screenshots in timelapse
)
```

---

## 🌐 Network Security

### Telegram Communication

- **Encryption**: All bot communication uses Telegram's MTProto (encrypted)
- **Webhooks**: Not used — long polling only (no open ports)
- **API Calls**: HTTPS only to `api.telegram.org`

### Outbound Connections

| Module | Destination | Purpose |
|--------|-------------|---------|
| `files` `/download` | User-provided URLs | File downloads |
| `ffmpeg` `/ffmpeg_install` | `gyan.dev` | FFmpeg binary |
| `system` `/status` | None (local) | System info |

### Firewall Rules (Windows)

```powershell
# Allow only Telegram API
New-NetFirewallRule -DisplayName "OwlBot Telegram" `
  -Direction Outbound -Action Allow `
  -RemoteAddress 149.154.160.0/20, 91.108.4.0/22 `
  -Protocol TCP -RemotePort 443

# Block all other outbound (optional, strict)
New-NetFirewallRule -DisplayName "OwlBot Block Other" `
  -Direction Outbound -Action Block `
  -Program "C:\Python\python.exe"
```

---

## 🔍 Audit Logging

### Enable Full Logging

```python
import logging

# Structured JSON logging for SIEM
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", '
           '"module": "%(name)s", "message": "%(message)s"}',
    handlers=[
        logging.FileHandler("owlbot_audit.log"),
        logging.StreamHandler(),
    ]
)

bot = OwlBot(..., log_level="INFO", log_file="owlbot.log")
```

### Key Events to Monitor

| Event | Log Pattern | Severity |
|-------|-------------|----------|
| Bot start/stop | `OwlBot v.* starting\|stopping` | INFO |
| User command | `Executing /<command> for user <id>` | INFO |
| Auth failure | `Unauthorized access attempt from <id>` | WARNING |
| Command error | `Error in /<command>: <error>` | ERROR |
| File download | `Downloading <url> to <path>` | INFO |
| Process kill | `Killed <n> processes: <names>` | WARNING |
| System shutdown | `Shutdown initiated by user <id>` | CRITICAL |

### Log Retention

```bash
# Rotate logs daily, keep 30 days (Linux/macOS)
# /etc/logrotate.d/owlbot
/var/log/owlbot/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🖥️ System Hardening

### Run as Non-Admin (Recommended)

```powershell
# Create dedicated user
New-LocalUser -Name "owlbot" -NoPassword
Add-LocalGroupMember -Group "Users" -Member "owlbot"

# Run as that user
runas /user:owlbot python bot.py
```

### Windows Service (Production)

```cmd
# Install as service (NSSM)
nssm install OwlBot
nssm set OwlBot Application C:\Python\python.exe
nssm set OwlBot AppParameters C:\owlbot\bot.py
nssm set OwlBot AppDirectory C:\owlbot
nssm set OwlBot ObjectName owlbot  # Service account
nssm set OwlBot Type SERVICE_AUTO_START
nssm start OwlBot
```

### Linux Systemd Service

```ini
# /etc/systemd/system/owlbot.service
[Unit]
Description=OwlBot Telegram Remote Control
After=network.target

[Service]
Type=simple
User=owlbot
Group=owlbot
WorkingDirectory=/opt/owlbot
ExecStart=/opt/owlbot/.venv/bin/python bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/owlbot/logs /opt/owlbot/downloads
CapabilityBoundingSet=

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now owlbot
sudo journalctl -u owlbot -f
```

---

## 🔐 Secure Deployment Checklist

### Pre-Deployment

- [ ] Token stored in environment variable / secret manager
- [ ] `authorized_users` contains only trusted IDs
- [ ] `protected_processes` includes all critical system processes
- [ ] `log_level` set to `INFO` (not `DEBUG` in production)
- [ ] `log_file` configured with rotation
- [ ] Unnecessary modules disabled
- [ ] File size limits configured appropriately

### Runtime

- [ ] Bot runs as non-root / non-Admin user
- [ ] Firewall restricts outbound connections
- [ ] Audit logs forwarded to SIEM / log aggregator
- [ ] Monitoring alerts on auth failures / shutdown commands
- [ ] Regular token rotation (monthly recommended)

### Incident Response

- [ ] Revoke token immediately if compromised: `@BotFather` → `/revoke`
- [ ] Check audit logs for unauthorized commands
- [ ] Review downloaded files in `downloads/` directory
- [ ] Rotate all credentials

---

## 🐛 Vulnerability Reporting

Found a security issue? Please report responsibly:

1. **Do not** open a public issue
2. Email: **security@sepehrhi.ir** (or GitHub Security Advisories)
3. Include: Description, reproduction steps, impact assessment
4. We'll acknowledge within 48 hours and coordinate fix

---

## 📋 Compliance Notes

| Standard | Coverage |
|----------|----------|
| **Principle of Least Privilege** | ✅ User whitelisting, protected processes |
| **Audit Logging** | ✅ Structured logs, all commands logged |
| **Secrets Management** | ✅ Env vars, keyring, Docker secrets support |
| **Encryption in Transit** | ✅ Telegram MTProto / HTTPS |
| **Input Validation** | ✅ Path traversal, size limits, type validation |
| **Secure Defaults** | ✅ Conservative defaults, explicit opt-in for risky features |

---

## 📚 Related Docs

- [Configuration Reference](CONFIGURATION.md) — All config options
- [Module Reference](MODULES.md) — Command details
- [Getting Started](GETTING_STARTED.md) — Installation guide
- [API Reference](API.md) — Programmatic API