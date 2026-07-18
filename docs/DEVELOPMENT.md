# 🛠️ Development Guide

Guide for contributing to OwlBot — setup, testing, code style, and release process.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- FFmpeg (for media features)
- Windows for full module testing

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/sepehrHi/OwlBot.git
cd OwlBot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in development mode with all extras
pip install -e .[dev,all]

# Verify installation
pytest -v
flake8 src tests
owlbot --help
```

---

## 📁 Project Structure

```
OwlBot/
├── src/
│   └── owlbot/
│       ├── __init__.py          # Package exports, version
│       ├── __main__.py          # CLI entry point
│       ├── config/              # Configuration
│       │   └── __init__.py      # BotConfig, constants
│       ├── core/                # Core bot logic
│       │   ├── __init__.py
│       │   ├── bot.py           # Main OwlBot class
│       │   ├── decorators.py    # @authorized_only, @safe_reply
│       │   ├── help.py          # Dynamic help generator
│       │   └── utils.py         # Shared utilities
│       ├── modules/             # Feature modules
│       │   ├── __init__.py      # Module registry
│       │   ├── base.py          # BaseModule class
│       │   ├── system.py
│       │   ├── screen.py
│       │   ├── audio.py
│       │   ├── files.py
│       │   ├── input.py
│       │   ├── monitoring.py
│       │   ├── network.py
│       │   ├── processes.py
│       │   └── ffmpeg.py
│       └── platform/
│           ├── __init__.py
│           └── telegram.py      # Telegram adapter
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_config.py
│   ├── test_bot.py
│   ├── test_cli.py
│   ├── test_utils.py
│   └── test_monitoring.py
├── examples/                    # Example scripts
│   ├── minimum_example.py
│   └── my_owlbot_script.py
├── docs/                        # Documentation
│   ├── GETTING_STARTED.md
│   ├── CONFIGURATION.md
│   ├── MODULES.md
│   ├── API.md
│   ├── SECURITY.md
│   ├── DEVELOPMENT.md
│   └── EXAMPLES.md
├── .github/
│   └── workflows/
│       └── python-package.yml   # CI/CD
├── pyproject.toml               # Project metadata (PEP 621)
├── setup.py                     # Setuptools shim
├── README.md                    # Main readme (English)
├── LICENSE
├── CHANGELOG.md
└── requirements-dev.txt
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests with coverage
pytest --cov=owlbot --cov-report=term-missing

# Specific test file
pytest tests/test_config.py -v

# Specific test
pytest tests/test_config.py::test_config_validation -v

# Watch mode (requires pytest-watch)
ptw tests/
```

### Test Structure

```python
# tests/test_config.py
import pytest
from owlbot.config import BotConfig

def test_config_validation():
    """Invalid token should raise ValueError."""
    with pytest.raises(ValueError, match="token must not be empty"):
        BotConfig(token="", authorized_users=[123])

def test_config_defaults():
    """Defaults should be applied."""
    config = BotConfig(token="123:ABC", authorized_users=[123])
    assert config.log_level == "INFO"
    assert config.log_file == "owlbot.log"
    assert config.enable_logging is True
```

### Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from owlbot import OwlBot
from owlbot.config import BotConfig

@pytest.fixture
def bot_config():
    return BotConfig(
        token="123456:TEST_TOKEN",
        authorized_users=[123456789],
        enable_logging=False,
    )

@pytest.fixture
def bot(bot_config):
    return OwlBot(config=bot_config)

@pytest.fixture
def mock_ctx():
    ctx = AsyncMock()
    ctx.user_id = 123456789
    ctx.chat_id = 123456789
    ctx.args = ""
    return ctx
```

### Mocking External Dependencies

```python
# Mock psutil for cross-platform tests
@pytest.fixture(autouse=True)
def mock_psutil(monkeypatch):
    import psutil
    monkeypatch.setattr(psutil, "cpu_percent", lambda *a, **k: 42.0)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: ...)

# Mock Telegram API
@pytest.fixture
def mock_telegram(monkeypatch):
    import telebot
    monkeypatch.setattr(telebot, "TeleBot", AsyncMock)
```

---

## 🎨 Code Style

### Linting & Formatting

```bash
# Lint (CI uses this)
flake8 src tests

# Format (recommended)
black src tests
isort src tests

# Type checking
mypy src
```

### Configuration

```ini
# .flake8
[flake8]
max-line-length = 127
max-complexity = 12
exclude = .git,__pycache__,build,dist,.venv,*.egg-info

# pyproject.toml (partial)
[tool.black]
line-length = 127
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 127
```

### Style Rules

| Rule | Standard |
|------|----------|
| Indent | 4 spaces |
| Line length | 127 chars |
| Quotes | Double (`"`) |
| Imports | Stdlib → Third-party → Local |
| Type hints | Required for public API |
| Docstrings | Google style (PEP 257) |
| Naming | `snake_case` functions, `PascalCase` classes, `UPPER_CASE` constants |

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

---

## 📝 Adding a New Module

### 1. Create Module File

```python
# src/owlbot/modules/weather.py
"""Weather module — fetch current weather and forecasts."""
from __future__ import annotations
from owlbot.modules.base import BaseModule
from owlbot.core.decorators import authorized_only, safe_reply
from owlbot.config import BotConfig

class WeatherModule(BaseModule):
    name = "weather"
    description = "Weather information"
    commands = {
        "weather": "Current weather for city",
        "forecast": "3-day forecast",
    }
    
    def __init__(self, bot, config: BotConfig) -> None:
        super().__init__(bot, config)
        self.api_key = config.weather_api_key  # Add to BotConfig
    
    @authorized_only
    @safe_reply
    def cmd_weather(self, ctx):
        """Usage: /weather <city>"""
        city = ctx.args or "Tehran"
        # ... fetch weather ...
        ctx.reply(f"🌤️ {city}: 22°C, Sunny")
    
    @authorized_only
    @safe_reply
    def cmd_forecast(self, ctx):
        """Usage: /forecast <city>"""
        ctx.reply("📅 3-day forecast...")

# Auto-register (optional)
from owlbot.modules import register_module
register_module(WeatherModule)
```

### 2. Add to Module Registry

```python
# src/owlbot/modules/__init__.py
from owlbot.modules.weather import WeatherModule

# Add to AVAILABLE_MODULES
AVAILABLE_MODULES = [
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring",
    "network", "ffmpeg", "weather",  # Add here
]
```

### 3. Add Config (if needed)

```python
# src/owlbot/config/__init__.py
@dataclass
class BotConfig:
    ...
    weather_api_key: str = ""  # New field
    
    def __post_init__(self):
        ...
        if "weather" in self.modules and not self.weather_api_key:
            raise ValueError("weather_api_key required for weather module")
```

### 4. Add Tests

```python
# tests/test_weather.py
import pytest
from owlbot.modules.weather import WeatherModule

def test_weather_module_load(bot):
    module = WeatherModule(bot, bot.config)
    assert module.name == "weather"
    assert "weather" in module.commands
```

### 5. Update Documentation

- Add to `docs/MODULES.md`
- Add commands to `src/owlbot/core/help.py`
- Update `README.md` module table

---

## 🔄 Release Process

### Versioning

Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

### Release Checklist

```bash
# 1. Update version
# pyproject.toml: version = "1.1.0"
# src/owlbot/__init__.py: __version__ = "1.1.0"

# 2. Update CHANGELOG.md
# ## [1.1.0] - 2024-01-15
# ### Added
# - Weather module

# 3. Run tests
pytest -v
flake8 src tests
mypy src

# 4. Build
pip install build
python -m build

# 5. Test package
pip install dist/owlbot_remote-1.1.0-py3-none-any.whl
owlbot --help

# 6. Publish to PyPI
pip install twine
twine upload dist/*

# 7. Git tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 8. GitHub Release
# Go to GitHub → Releases → Create new release
# Tag: v1.1.0
# Title: OwlBot v1.1.0
# Description: Copy from CHANGELOG.md
```

### CI/CD Pipeline (`.github/workflows/python-package.yml`)

```yaml
name: Python Package

on:
  push:
    tags: ['v*']
  pull_request:

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[dev,all]
      - run: flake8 src tests
      - run: mypy src
      - run: pytest --cov=owlbot

  publish:
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

---

## 🐛 Debugging

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

bot = OwlBot(..., log_level="DEBUG")
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Module not loading | Check `AVAILABLE_MODULES`, dependencies installed |
| Telegram 409 Conflict | Another instance running — use `drop_pending_updates=True` |
| FFmpeg not found | Install FFmpeg, add to PATH |
| Permission denied | Run as Admin (Windows) or check file permissions |
| ImportError | `pip install -e .[all]` in project root |

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

bot.run()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

---

## 📋 Contribution Guidelines

### Before Contributing

1. Check existing issues/PRs
2. Open an issue for discussion (features/bugs)
3. Fork and create feature branch

### Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Lint passes (`flake8 src tests`)
- [ ] Type check passes (`mypy src`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped (if applicable)

### Code Review Criteria

- Correctness & edge cases
- Test coverage
- Code style consistency
- Performance impact
- Security implications
- Documentation completeness

---

## 📚 Related Docs

- [API Reference](API.md)
- [Module Reference](MODULES.md)
- [Configuration](CONFIGURATION.md)
- [Security](SECURITY.md)