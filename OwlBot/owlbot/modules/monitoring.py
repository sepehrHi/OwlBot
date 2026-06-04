"""
Monitoring module — /monitor <cpu|ram|disk|temp>, /stopmonitor
"""
from __future__ import annotations

import threading
import time

import psutil
import wmi

from owlbot.modules.base import BaseModule


class MonitoringModule(BaseModule):
    name = "monitoring"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._active = False
        self._thread: threading.Thread | None = None

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["monitor"])
        @auth
        @safe
        def cmd_monitor(message):
            if self._active:
                bot.reply_to(message, "⚠️ Monitoring already running. Use /stopmonitor first.")
                return
            parts = message.text.split()
            if len(parts) < 2 or parts[1] not in ("cpu", "ram", "disk", "temp"):
                bot.reply_to(message, "Usage: /monitor <cpu|ram|disk|temp>")
                return
            self._active = True
            self._thread = threading.Thread(
                target=self._worker, args=(message.chat.id, parts[1]), daemon=True
            )
            self._thread.start()
            bot.reply_to(message, f"📊 Monitoring {parts[1].upper()} every {self.config.monitor_interval}s. Use /stopmonitor to stop.")

        @bot.message_handler(commands=["stopmonitor"])
        @auth
        @safe
        def cmd_stopmonitor(message):
            if not self._active:
                bot.reply_to(message, "⚠️ No active monitoring.")
                return
            self._active = False
            bot.reply_to(message, "🛑 Monitoring stopped.")

    def _worker(self, chat_id: int, param: str) -> None:
        cfg = self.config
        bot = self.bot
        c = wmi.WMI()
        try:
            while self._active:
                if param == "cpu":
                    pct = psutil.cpu_percent(interval=1)
                    bot.send_message(chat_id, f"📊 CPU: {pct}%")
                elif param == "ram":
                    r = psutil.virtual_memory()
                    bot.send_message(
                        chat_id,
                        f"📊 RAM: {r.percent}%  ({r.used/1024**3:.2f} / {r.total/1024**3:.2f} GB)",
                    )
                elif param == "disk":
                    d = psutil.disk_usage("/")
                    bot.send_message(
                        chat_id,
                        f"📊 Disk: {d.percent}%  ({d.used/1024**3:.2f} / {d.total/1024**3:.2f} GB)",
                    )
                elif param == "temp":
                    probes = c.Win32_TemperatureProbe()
                    if probes:
                        t = probes[0].CurrentReading / 10.0
                        bot.send_message(chat_id, f"🌡️ Temperature: {t:.1f}°C")
                    else:
                        bot.send_message(chat_id, "❌ Temperature sensor not available.")
                time.sleep(cfg.monitor_interval)
        except Exception as exc:
            bot.send_message(chat_id, f"❌ Monitoring error: {exc}")
        finally:
            self._active = False
