## 🦉 OwlBot v1.0.1 — Second Release: Animations & Polish

> **PEP 440 version:** `1.0.1` · **Requires:** Python ≥ 3.11 · **OS:** Windows (core modules are cross‑platform)

A polish release focused on live status feedback for long‑running commands and a more reliable FFmpeg download path.

نسخه‌ی دوم OwlBot — تمرکز روی بازخورد زنده برای دستورات طولانی و دانلود پایدارتر FFmpeg.

---

### 🆕 Added · اضافه‌شده‌ها

- Animated "در حال پردازش…" progress message (auto-edited in place) for: `/status`, `/uptime`, `/webcam`, `/ffmpeg_install`, `/netcheck`, `/screenshot`, `/wifiscan`.
- Automatic retry with backoff (3 attempts) and timeout for FFmpeg downloads.
- FFmpeg download link now points to a specific Gyan.dev essentials build instead of a `latest` URL that could change underneath users.

### 🛠️ Changed · تغییرات

- `SystemModule.register` split into helper functions `_build_status_text()` and `_build_uptime_text()` to resolve a flake8 C901 complexity warning.
- `_download_with_retry` helper added to `ffmpeg.py`.
- `README.md` and docs updated.

### 🐛 Fixed · رفع‌شده‌ها

- FFmpeg link changed from `latest` to a pinned release (Gyan.dev essentials build).
- `flake8 W605` invalid escape sequence in a docstring.
- Issue #1: verify the FFmpeg download link.

---

### 📥 Installation · نصب

```bash
pip install owlbot_remote-1.0.1-py3-none-any.whl
# or, from source:
pip install -e .
```

### 🧪 Verify it yourself · خودتان تأیید کنید

```bash
pip install -e ".[dev]"
pytest -v
flake8 src tests
```

**Full diff:** https://github.com/sepehrHi/OwlBot/compare/v1.0.0-beta.0...v1.0.1

[1.0.1]: https://github.com/sepehrHi/OwlBot/releases/tag/v1.0.1
