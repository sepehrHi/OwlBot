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

    def register(self) -> None:  # noqa: C901
        bot, auth, safe = self.bot, self.auth, self.safe
        cfg = self.config

        @bot.message_handler(commands=["tasklist"])
        @auth
        @safe
        def cmd_tasklist(message: object) -> None:
            bot.send_chat_action(message.chat.id, "typing")
            procs = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                try:
                    mem_mb = (proc.info["memory_info"].rss or 0) / 1024 ** 2
                    procs.append((proc.info["name"] or "", proc.info["pid"], mem_mb))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            procs.sort(key=lambda p: p[0].lower())
            lines = [f"⚙️  Running Processes ({len(procs)} total)\n"]
            lines += [f"  {pid:>6}  {name:<30}  {mem:>8.1f} MB" for name, pid, mem in procs]
            send_large_text(bot, message.chat.id, "\n".join(lines), "tasklist.txt")

        @bot.message_handler(commands=["killtask"])
        @auth
        @safe
        def cmd_killtask(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: `/killtask <process_name.exe>`", parse_mode="Markdown")
                return
            target = parts[1].strip().lower()
            if target in cfg.protected_processes:
                bot.reply_to(message, f"🛡️ Protected process — cannot kill: `{target}`", parse_mode="Markdown")
                return
            bot.send_chat_action(message.chat.id, "typing")
            killed = 0
            for proc in psutil.process_iter(["name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() == target:
                        proc.kill()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if killed:
                bot.reply_to(message, f"✅ Killed *{killed}* instance(s) of `{target}`.", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"⚠️ No process found: `{target}`", parse_mode="Markdown")

        @bot.message_handler(commands=["run"])
        @auth
        @safe
        def cmd_run(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: `/run <program>`", parse_mode="Markdown")
                return
            subprocess.Popen(parts[1].split(), shell=True)
            bot.reply_to(message, f"🚀 *Launched:* `{parts[1]}`", parse_mode="Markdown")

        @bot.message_handler(commands=["cmd"])
        @auth
        @safe
        def cmd_run_cmd(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: `/cmd <command>`", parse_mode="Markdown")
                return
            bot.send_chat_action(message.chat.id, "typing")
            result = subprocess.run(
                parts[1], shell=True, capture_output=True, text=True, timeout=30,
            )
            output = (result.stdout or "") + (result.stderr or "")
            send_large_text(
                bot, message.chat.id,
                output or "✅ Command executed (no output).",
                "cmd_output.txt",
            )

        @bot.message_handler(commands=["script"])
        @auth
        @safe
        def cmd_script(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: `/script <python code>`", parse_mode="Markdown")
                return
            import contextlib
            import io
            bot.send_chat_action(message.chat.id, "typing")
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    exec(parts[1], {})  # noqa: S102
            except Exception as exc:
                buf.write(f"\nException: {exc}")
            output = buf.getvalue()
            send_large_text(
                bot, message.chat.id,
                output or "✅ Executed (no output).",
                "script_output.txt",
            )

        @bot.message_handler(commands=["runscript"])
        @auth
        @safe
        def cmd_runscript(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: `/runscript <path.py>`", parse_mode="Markdown")
                return
            bot.send_chat_action(message.chat.id, "typing")
            result = subprocess.run(
                [sys.executable, parts[1].strip()],
                capture_output=True, text=True, timeout=60,
            )
            output = (result.stdout or "") + (result.stderr or "")
            send_large_text(
                bot, message.chat.id,
                output or "✅ Script done (no output).",
                "script_output.txt",
            )
