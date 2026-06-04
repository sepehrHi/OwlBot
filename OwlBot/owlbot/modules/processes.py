"""
Processes module — /tasklist, /killtask, /run, /cmd, /script, /runscript
"""
from __future__ import annotations

import subprocess
import sys

import psutil

from owlbot.core.utils import send_large_text
from owlbot.modules.base import BaseModule


class ProcessesModule(BaseModule):
    name = "processes"

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe
        cfg = self.config

        @bot.message_handler(commands=["tasklist"])
        @auth
        @safe
        def cmd_tasklist(message):
            lines = ["⚙️ Running Processes\n"]
            for proc in sorted(psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]),
                               key=lambda p: p.info["name"] or ""):
                try:
                    mem_mb = proc.info["memory_info"].rss / 1024**2
                    lines.append(f"{proc.info['pid']:>6}  {proc.info['name']:<30}  {mem_mb:>7.1f} MB")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            send_large_text(bot, message.chat.id, "\n".join(lines), "tasklist.txt")

        @bot.message_handler(commands=["killtask"])
        @auth
        @safe
        def cmd_killtask(message):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /killtask <process_name.exe>")
                return
            target = parts[1].strip().lower()
            if target in cfg.protected_processes:
                bot.reply_to(message, f"🛡️ Protected process — cannot kill: {target}")
                return
            killed = 0
            for proc in psutil.process_iter(["name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() == target:
                        proc.kill()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if killed:
                bot.reply_to(message, f"✅ Killed {killed} instance(s) of {target}.")
            else:
                bot.reply_to(message, f"⚠️ No process found: {target}")

        @bot.message_handler(commands=["run"])
        @auth
        @safe
        def cmd_run(message):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /run <program>")
                return
            subprocess.Popen(parts[1].split(), shell=True)
            bot.reply_to(message, f"🚀 Launched: {parts[1]}")

        @bot.message_handler(commands=["cmd"])
        @auth
        @safe
        def cmd_run_cmd(message):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /cmd <command>")
                return
            result = subprocess.run(
                parts[1], shell=True, capture_output=True, text=True, timeout=30
            )
            output = (result.stdout or "") + (result.stderr or "")
            send_large_text(bot, message.chat.id, output or "✅ Command executed (no output).", "cmd_output.txt")

        @bot.message_handler(commands=["script"])
        @auth
        @safe
        def cmd_script(message):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /script <python code>")
                return
            import io, contextlib
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    exec(parts[1], {})  # noqa: S102
            except Exception as exc:
                buf.write(f"\nException: {exc}")
            output = buf.getvalue()
            send_large_text(bot, message.chat.id, output or "✅ Executed (no output).", "script_output.txt")

        @bot.message_handler(commands=["runscript"])
        @auth
        @safe
        def cmd_runscript(message):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /runscript <path.py>")
                return
            path = parts[1].strip()
            result = subprocess.run(
                [sys.executable, path], capture_output=True, text=True, timeout=60
            )
            output = (result.stdout or "") + (result.stderr or "")
            send_large_text(bot, message.chat.id, output or "✅ Script done (no output).", "script_output.txt")
