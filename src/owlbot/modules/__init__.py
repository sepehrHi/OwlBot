"""
owlbot/modules/__init__.py
Registry of all available modules.
Lazy-imports modules to avoid ImportError on non-Windows or missing deps.
"""
from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from owlbot.modules.base import BaseModule

logger = logging.getLogger("owlbot.modules")

MODULE_REGISTRY: dict[str, type[BaseModule]] = {}


def _register_modules() -> None:
    """Populate MODULE_REGISTRY with available modules using lazy imports."""
    # Cross-platform modules — always available
    from owlbot.modules.system import SystemModule
    from owlbot.modules.processes import ProcessesModule
    from owlbot.modules.monitoring import MonitoringModule
    from owlbot.modules.network import NetworkModule
    from owlbot.modules.ffmpeg import FFmpegModule
    from owlbot.modules.ip import IPModule

    MODULE_REGISTRY.update({
        "system": SystemModule,
        "processes": ProcessesModule,
        "monitoring": MonitoringModule,
        "network": NetworkModule,
        "ffmpeg": FFmpegModule,
        "ip": IPModule,
    })

    # UI modules — require opencv, pyautogui, numpy (optional)
    try:
        from owlbot.modules.screen import ScreenModule
        from owlbot.modules.files import FilesModule
        MODULE_REGISTRY.update({
            "screen": ScreenModule,
            "files": FilesModule,
        })
    except ImportError as exc:
        logger.info("UI modules (screen/files) unavailable — missing dependency: %s", exc)

    # Windows-only modules
    if sys.platform == "win32":
        try:
            from owlbot.modules.audio import AudioModule
            MODULE_REGISTRY["audio"] = AudioModule
        except ImportError as exc:
            logger.info("Audio module unavailable — missing dependency: %s", exc)
        try:
            from owlbot.modules.input import InputModule
            MODULE_REGISTRY["input"] = InputModule
        except ImportError as exc:
            logger.info("Input module unavailable — missing dependency: %s", exc)


_register_modules()

__all__ = ["MODULE_REGISTRY"]
