"""
OwlBot Configuration — BotConfig dataclass with validation.
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from typing import FrozenSet, List, Optional

AVAILABLE_MODULES = frozenset({
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring", "network", "ffmpeg", "ip",
})

#: Modules that only make sense on Windows (need Win32-only optional deps).
WINDOWS_ONLY_MODULES = frozenset({"audio", "input"})

#: Modules that work on every supported platform.
CROSS_PLATFORM_MODULES = AVAILABLE_MODULES - WINDOWS_ONLY_MODULES

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

__all__ = [
    "BotConfig",
    "AVAILABLE_MODULES",
    "WINDOWS_ONLY_MODULES",
    "CROSS_PLATFORM_MODULES",
    "VALID_LOG_LEVELS",
]

_config_logger = logging.getLogger("owlbot.config")


@dataclass
class BotConfig:
    """
    Central configuration for OwlBot.

    All settings have safe defaults. Validation happens in ``__post_init__``
    and raises :class:`ValueError` on invalid input so misconfiguration is
    caught early instead of failing later inside the bot loop.
    """
    token: str
    authorized_users: List[int]
    platform: str = "telegram"
    modules: List[str] = field(default_factory=lambda: list(AVAILABLE_MODULES))

    # Logging
    #: Minimum severity that gets logged. Must be one of ``VALID_LOG_LEVELS``.
    log_level: str = "INFO"
    #: Path to the log file. Set to ``None`` or ``""`` to disable file
    #: logging entirely (no log file will be created on disk).
    log_file: Optional[str] = "owlbot.log"
    #: Master switch. When ``False`` no logging handler is configured at
    #: all (console or file) and OwlBot stays silent.
    enable_logging: bool = True

    # Audio
    audio_sample_rate: int = 16_000
    audio_chunk_size: int = 1_024
    audio_channels: int = 1
    max_record_duration: int = 120
    min_record_duration: int = 1

    # File transfer
    max_file_size_mb: int = 50
    max_download_mb: int = 20
    max_timelapse_count: int = 60

    # Screen / stream
    stream_fps: int = 5
    screenshot_quality: int = 85
    stream_jpeg_quality: int = 50
    stream_frame_delay: float = 0.2
    stream_photo_interval: float = 1.0

    # Monitoring
    monitor_interval: int = 10

    # Protected processes (cannot be killed)
    protected_processes: FrozenSet[str] = field(default_factory=lambda: frozenset({
        "system", "svchost.exe", "csrss.exe", "winlogon.exe",
        "lsass.exe", "services.exe", "smss.exe", "wininit.exe",
        "dwm.exe", "ntoskrnl.exe",
    }))

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("Bot token must not be empty.")
        if not self.authorized_users:
            raise ValueError("At least one authorized user is required.")

        unknown = set(self.modules) - AVAILABLE_MODULES
        if unknown:
            raise ValueError(
                f"Unknown modules: {sorted(unknown)}. Valid: {sorted(AVAILABLE_MODULES)}"
            )

        log_level_upper = self.log_level.upper() if self.log_level else "INFO"
        if log_level_upper not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log_level: {self.log_level!r}. Valid: {sorted(VALID_LOG_LEVELS)}"
            )
        self.log_level = log_level_upper

        # An empty string is treated the same as None: "no log file".
        if not self.log_file:
            self.log_file = None

        if sys.platform != "win32":
            win_only_requested = set(self.modules) & WINDOWS_ONLY_MODULES
            if win_only_requested:
                _config_logger.warning(
                    "Modules %s require Windows and will be skipped on %s.",
                    sorted(win_only_requested), sys.platform,
                )
                self.modules = [m for m in self.modules if m not in win_only_requested]
