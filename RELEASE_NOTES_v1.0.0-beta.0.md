## 🦉 OwlBot v1.0.0-beta.0 — First Public Release

> **PEP 440 version:** `1.0.0b0` · **Requires:** Python ≥ 3.11 · **OS:** Windows (core modules are cross‑platform)

The very first tagged, installable release of OwlBot — a modular Telegram remote‑control agent for Windows, rebuilt from the ground up to follow the official Python packaging & contribution standards (`python.org`, `devguide.python.org`, `packaging.python.org`).

این اولین نسخه‌ی رسمی و قابل‌نصب OwlBot — یک ایجنت ماژولار کنترل‌ازراه‌دور تلگرامی برای ویندوز — که کاملاً طبق استانداردهای رسمی بسته‌بندی و مشارکت پایتون (`python.org`, `devguide.python.org`, `packaging.python.org`) بازسازی شده.

---

### ✨ Highlights · نکات برجسته

- 📦 **Standard `src/` package layout** built on `pyproject.toml` (PEP 621) — installable via `pip install -e .` or as a wheel.
  ساختار استاندارد پکیج (`src/`) مطابق PEP 621 — نصب‌پذیر با `pip install -e .` یا به‌صورت wheel.
- 🔇 **Fully configurable logging** — keep the default console+file logging, disable *just* the log file, or go completely silent.
  سیستم لاگ کاملاً قابل‌تنظیم — لاگ پیش‌فرض (کنسول+فایل)، فقط بی‌فایل، یا کاملاً بی‌صدا.
- 🧪 **45 automated tests** (`pytest`) covering config validation, logging behavior, the CLI, and monitoring — zero real network calls.
  ۴۵ تست خودکار (`pytest`) — بدون هیچ تماس شبکه‌ای واقعی.
- 🧹 **Zero lint warnings** — `flake8` (style + complexity) is 100% clean across `src/` and `tests/`.
  صفر هشدار لینت — `flake8` کاملاً تمیزه.
- ⚙️ **Real CI/CD on GitHub Actions** — lint → test (Python 3.11 & 3.12) → build → `twine check`, all green.
  CI/CD واقعی روی GitHub Actions — لینت ← تست ← build ← `twine check`، همه سبز.

---

### 🆕 Added · اضافه‌شده‌ها

- Standard `src/owlbot/...` package layout per the packaging tutorial, replacing the old flat layout.
- `pyproject.toml` (PEP 621) as the single source of package metadata; `setup.py` kept only as a compatibility shim.
- Modular install extras: `[ui]`, `[windows]`, `[all]`, `[dev]`.
- New logging controls on `BotConfig` / `OwlBot` / CLI:
  - `log_level` — now validated against `DEBUG|INFO|WARNING|ERROR|CRITICAL`.
  - `log_file` — set to `None`/`""` to skip creating a log file on disk.
  - `enable_logging` — set to `False` to fully silence OwlBot (no console, no file).
  - CLI flags: `--log-level`, `--log-file`, `--no-log-file`, `--disable-logging`.
- Full `tests/` suite: `test_config.py`, `test_bot.py`, `test_cli.py`, `test_utils.py`, `test_monitoring.py`, `conftest.py`.
- Real `.flake8` config file (`max-line-length=127`, `max-complexity=12`) — previously `[tool.flake8]` in `pyproject.toml` was silently ignored by flake8.
- `docs/PYTHON_STANDARDS_SKILL.md` — the coding-standards checklist used to review this codebase (PEP 8, PEP 257, devguide contributing, packaging).
- `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Rewritten GitHub Actions workflows:
  - `python-package.yml` — now actually installs the package + `[dev]` extra, runs the full `pytest` suite with coverage, lints `src` **and** `tests`, builds sdist/wheel in a dedicated job, runs `twine check`, uploads build artifacts, and supports manual `workflow_dispatch` runs.
  - `python-publish.yml` — added `twine check` before publishing to PyPI via trusted OIDC publishing.

### 🛠️ Fixed · رفع‌شده‌ها

- `BotConfig.__post_init__` had duplicated/inverted validation logic and a dead variable (`_WIN_ONLY_MODULES`) that was defined but never used — simplified into a single, correct validation path.
- Windows-only modules (`audio`, `input`) are now correctly filtered out on non-Windows platforms.
- Fixed a stray `platforms/telegram.py` (plural) path reference in the README — the real path is `platform/telegram.py` (singular).
- Removed an unused `typing.List` import in `platform/telegram.py`.
- Resolved all 7 `flake8` C901 complexity warnings: `monitoring.py`'s worker loop was genuinely refactored into small, pure, independently‑tested metric readers (`_read_cpu`, `_read_ram`, `_read_disk`, `_read_temp`); the remaining 6 (`register()` methods, which are flat lists of independent command handlers rather than nested logic) are documented with `# noqa: C901`.
- Recovered `.github/workflows/` and the full `src/` tree after they were accidentally deleted directly on GitHub.

### 🔒 Security · امنیت

Deep input hardening (rate limiting, stricter validation, etc.) is intentionally deferred to a future release, as agreed for this beta.
سخت‌گیری‌های امنیتی عمیق (rate limiting، اعتبارسنجی سخت‌گیرانه‌تر و ...) آگاهانه به نسخه‌ی بعدی موکول شده.

---

### 📥 Installation · نصب

```bash
pip install owlbot_remote-1.0.0b0-py3-none-any.whl
# or, from source:
pip install -e .
```

### 🧪 Verify it yourself · خودتان تأیید کنید

```bash
pip install -e ".[dev]"
pytest -v
flake8 src tests
```

**Full diff:** https://github.com/sepehrHi/OwlBot/compare/e4e1b13...v1.0.0-beta.0
