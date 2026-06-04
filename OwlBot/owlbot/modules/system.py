"""
System module — /status, /uptime, /ping, /lock, /shutdown, /restart
"""
from __future__ import annotations

import ctypes
import os
import time

import psutil

from owlbot.core.utils import format_bytes, format_uptime
from owlbot.modules.base import BaseModule


class SystemModule(BaseModule):
    name = "system"

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["start", "help"])
        @auth
        @safe
        def cmd_help(message):
            bot.reply_to(message, _HELP_TEXT)

        @bot.message_handler(commands=["ping"])
        @auth
        @safe
        def cmd_ping(message):
            bot.reply_to(message, "🏓 Pong! Bot is online and responsive.")

        @bot.message_handler(commands=["lock"])
        @auth
        @safe
        def cmd_lock(message):
            ctypes.windll.user32.LockWorkStation()
            bot.reply_to(message, "🔒 Workstation locked.")

        @bot.message_handler(commands=["shutdown"])
        @auth
        @safe
        def cmd_shutdown(message):
            bot.reply_to(message, "🛑 Shutting down in 3 seconds...")
            os.system("shutdown /s /t 3")

        @bot.message_handler(commands=["restart"])
        @auth
        @safe
        def cmd_restart(message):
            bot.reply_to(message, "🔄 Restarting in 3 seconds...")
            os.system("shutdown /r /t 3")

        @bot.message_handler(commands=["status"])
        @auth
        @safe
        def cmd_status(message):
            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            bat  = psutil.sensors_battery()
            net  = psutil.net_io_counters()
            lines = [
                "📊 System Status",
                f"🖥️ CPU:  {cpu}%  (cores: {psutil.cpu_count()})",
                f"🧠 RAM:  {ram.percent}%  ({ram.used/1024**3:.2f} / {ram.total/1024**3:.2f} GB)",
                f"💾 Disk: {disk.percent}%  ({disk.used/1024**3:.2f} / {disk.total/1024**3:.2f} GB)",
                f"🌐 Net ↑ {format_bytes(net.bytes_sent)}  ↓ {format_bytes(net.bytes_recv)}",
            ]
            if bat:
                plug = "🔌 Plugged in" if bat.power_plugged else "🔋 On battery"
                lines.append(f"🔋 Battery: {bat.percent:.1f}%  ({plug})")
            else:
                lines.append("🔋 Battery: N/A (desktop)")
            bot.reply_to(message, "\n".join(lines))

        @bot.message_handler(commands=["uptime"])
        @auth
        @safe
        def cmd_uptime(message):
            elapsed = time.time() - psutil.boot_time()
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            bot.reply_to(
                message,
                f"⏰ Uptime: {format_uptime(elapsed)}\n"
                f"🖥️ CPU: {cpu}%\n"
                f"🧠 RAM: {ram.percent}%  ({ram.used/1024**3:.2f} / {ram.total/1024**3:.2f} GB)",
            )


_HELP_TEXT = """
🦉 Owl Remote Control Bot

🖥️ System
/status  — CPU, RAM, disk, battery
/uptime  — System uptime
/ping    — Check bot is alive
/lock    — Lock workstation
/shutdown — Shut down PC
/restart  — Restart PC

📸 Screen: /screenshot /webcam /timelapse /startstream /stopstream
⌨️ Input:  /type /move /mouse /hotkey /msg /mousepos
🔊 Audio:  /mute /unmute /volume /startrec /stoprec /playvoice
📁 Files:  /getfile /listdir /download /hide /show /file
⚙️ Procs:  /tasklist /killtask /run /cmd /script /runscript
📊 Mon:   /monitor /stopmonitor
🌐 Net:   /wifiscan /clipboard /media
""".strip()
