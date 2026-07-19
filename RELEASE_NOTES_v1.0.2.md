## 🦉 OwlBot v1.0.2 — IP & Location Module

> **PEP 440 version:** `1.0.2` · **Requires:** Python ≥ 3.11 · **OS:** Windows (core modules are cross‑platform)

A feature release: a brand-new `ip` module for IP lookups, VPN/proxy detection, and GPS/IP-based location.

نسخه‌ی سوم OwlBot — ماژول کاملاً جدید `ip` برای اطلاعات IP، تشخیص VPN و موقعیت مکانی (GPS/IP).

---

### 🆕 Added · اضافه‌شده‌ها

- **New `ip` module** — cross-platform, requires no new dependencies (`requests` was already a core dependency):
  - `/myip` — public IP + all local (LAN) IP addresses of the device
  - `/iplookup [ip]` — geo/ISP lookup for the device's own IP, or any given IP/hostname (via `ip-api.com`, free tier)
  - `/vpncheck` — heuristic VPN/proxy/hosting-IP detection
  - `/location` — send an IP-based location pin to the Telegram chat
  - `/gps` — best-effort **real** GPS/Wi-Fi-triangulated fix via Windows Location Services, with automatic fallback to IP-based location
  - `/locationlive <seconds>` — send a Telegram "live location" for a configurable duration (60–86400s)
- 15 new unit tests covering every pure helper in the `ip` module (no real network calls in tests)
- A **Disclaimer** section at the end of `README.md`: this library is provided for the user's own convenience to manage their own devices; any misuse is the user's responsibility, not the maintainer's.

### 🛠️ Changed · تغییرات

- `AVAILABLE_MODULES` and the module registry now include `ip`.
- `/help`, `docs/MODULES.md`, and `README.md` (features list, module table, project structure) updated with the full `ip` module documentation.

---

### 📥 Installation · نصب

```bash
pip install owlbot_remote-1.0.2-py3-none-any.whl
# or, from source:
pip install -e .
```

Enable it like any other module:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="YOUR_BOT_TOKEN",
    authorized_users=[123456789],
    modules=["system", "ip"],   # add "ip" to your module list
)
bot.run()
```

### 🧪 Verify it yourself · خودتان تأیید کنید

```bash
pip install -e ".[dev]"
pytest -v
flake8 src tests
```

### ⚠️ Privacy note

The `ip` and `/gps`/`/location` commands reveal the device's network
identity and approximate physical location. They are gated by the same
`authorized_users` allowlist as every other command in OwlBot — use them
only on devices you own or are explicitly authorized to manage. See the
Disclaimer in `README.md`.

---

**Full diff:** https://github.com/sepehrHi/OwlBot/compare/v1.0.1...v1.0.2

[1.0.2]: https://github.com/sepehrHi/OwlBot/releases/tag/v1.0.2
