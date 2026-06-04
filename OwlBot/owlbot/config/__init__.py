"""
OwlBot Configuration — BotConfig dataclass with validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


AVAILABLE_MODULES = frozenset({
    "system", "screen", "audio", "files",
    "input", "processes", "monitoring", "network",
})


@dataclass
class BotConfig:
    token: str
    authorized_users: List[int]
    platform: str = "telegram"
    modules: List[str] = field(default_factory=lambda: list(AVAILABLE_MODULES))

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "owlbot.log"

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
    protected_processes: frozenset = field(default_factory=lambda: frozenset({
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
            raise ValueError(f"Unknown modules: {unknown}. Valid: {AVAILABLE_MODULES}")
