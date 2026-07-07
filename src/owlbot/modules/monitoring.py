"""
Monitoring module — /monitor <cpu|ram|disk|temp>, /stopmonitor
"""
from __future__ import annotations

import logging
import sys
import threading
import time

import psutil

from owlbot.modules.base import BaseModule

logger = logging.getLogger("owlbot.modules.monitoring")


class MonitoringModule(BaseModule):
    name = "monitoring"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._active = False
        self._thread: threading.Thread | None = None

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["monitor"])
        @auth
        @safe
        def cmd_monitor(message: object) -> None:
            if self._active:
                bot.reply_to(message, "⚠️ Monitoring already running. Use /stopmonitor first.")
                return
            parts = message.text.split()  # type: ignore[attr-defined]
            if len(parts) < 2 or parts[1] not in ("cpu", "ram", "disk", "temp"):
                bot.reply_to(message, "Usage: /monitor <cpu|ram|disk|temp>")
                return
            self._active = True
            self._thread = threading.Thread(
                target=self._worker, args=(message.chat.id, parts[1]), daemon=True
            )
            self._thread.start()
            bot.reply_to(
                message,
                f"📊 Monitoring {parts[1].upper()} every {self.config.monitor_interval}s. "
                "Use /stopmonitor to stop.",
            )

        @bot.message_handler(commands=["stopmonitor"])
        @auth
        @safe
        def cmd_stopmonitor(message: object) -> None:
            if not self._active:
                bot.reply_to(message, "⚠️ No active monitoring.")
                return
            self._active = False
            bot.reply_to(message, "🛑 Monitoring stopped.")

    @staticmethod
    def _read_cpu() -> str:
        pct = psutil.cpu_percent(interval=1)
        return f"📊 CPU: {pct}%"

    @staticmethod
    def _read_ram() -> str:
        r = psutil.virtual_memory()
        return f"📊 RAM: {r.percent}%  ({r.used / 1024**3:.2f} / {r.total / 1024**3:.2f} GB)"

    @staticmethod
    def _read_disk() -> str:
        d = psutil.disk_usage("/")
        return f"📊 Disk: {d.percent}%  ({d.used / 1024**3:.2f} / {d.total / 1024**3:.2f} GB)"

    @staticmethod
    def _read_temp(wmi_client: object) -> str:
        if wmi_client is None:
            return "❌ Temperature monitoring requires Windows (wmi)."
        probes = wmi_client.Win32_TemperatureProbe()  # type: ignore[attr-defined]
        if not probes:
            return "❌ Temperature sensor not available."
        t = probes[0].CurrentReading / 10.0
        return f"🌡️ Temperature: {t:.1f}°C"

    @staticmethod
    def _init_wmi_client() -> object:
        if sys.platform != "win32":
            return None
        try:
            import wmi as wmi_mod
            return wmi_mod.WMI()
        except ImportError as exc:
            logger.info("wmi unavailable — temperature monitoring disabled: %s", exc)
            return None

    def _worker(self, chat_id: int, param: str) -> None:
        cfg = self.config
        bot = self.bot
        wmi_client = self._init_wmi_client() if param == "temp" else None
        readers = {
            "cpu": self._read_cpu,
            "ram": self._read_ram,
            "disk": self._read_disk,
            "temp": lambda: self._read_temp(wmi_client),
        }
        read_metric = readers[param]

        try:
            while self._active:
                bot.send_message(chat_id, read_metric())
                if param == "temp" and wmi_client is None:
                    return
                time.sleep(cfg.monitor_interval)
        except Exception as exc:
            bot.send_message(chat_id, f"❌ Monitoring error: {exc}")
        finally:
            self._active = False
