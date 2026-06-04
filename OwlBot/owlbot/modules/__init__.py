"""
owlbot/modules/__init__.py
Registry of all available modules.
"""
from owlbot.modules.audio import AudioModule
from owlbot.modules.files import FilesModule
from owlbot.modules.input import InputModule
from owlbot.modules.monitoring import MonitoringModule
from owlbot.modules.network import NetworkModule
from owlbot.modules.processes import ProcessesModule
from owlbot.modules.screen import ScreenModule
from owlbot.modules.system import SystemModule

MODULE_REGISTRY = {
    "system":     SystemModule,
    "screen":     ScreenModule,
    "audio":      AudioModule,
    "files":      FilesModule,
    "input":      InputModule,
    "processes":  ProcessesModule,
    "monitoring": MonitoringModule,
    "network":    NetworkModule,
}

__all__ = ["MODULE_REGISTRY"]
