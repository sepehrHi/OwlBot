"""
Network module — /wifiscan, /clipboard
Cross-platform module with lazy imports.
"""
from __future__ import annotations

import sys

from owlbot.core.utils import animate_message, finish_animation, internet_ok
from owlbot.modules.base import BaseModule


class NetworkModule(BaseModule):
    name = "network"

    def register(self) -> None:  # noqa: C901
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["netcheck"])
        @auth
        @safe
        def cmd_netcheck(message: object) -> None:
            bot.send_chat_action(message.chat.id, "typing")
            frames = [
                "📡 *Checking connection…* ⏳",
                "📡 *Checking connection…* ⏳⏳",
                "📡 *Checking connection…* ⏳⏳⏳",
            ]
            msg = animate_message(bot, message.chat.id, frames)
            ok = internet_ok()
            result = (
                "🌐 *Internet — ✅ connected*" if ok
                else "🌐 *Internet — ⚠️ no connection detected*"
            )
            finish_animation(bot, msg, message.chat.id, result)

        @bot.message_handler(commands=["wifiscan"])
        @auth
        @safe
        def cmd_wifiscan(message: object) -> None:
            if sys.platform != "win32":
                bot.reply_to(message, "❌ /wifiscan is Windows-only (requires pywifi).")
                return
            try:
                import pywifi
            except ImportError:
                bot.reply_to(message, "❌ pywifi not installed.\n`pip install pywifi`", parse_mode="Markdown")
                return

            bot.send_chat_action(message.chat.id, "find_location")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["📡 *Scanning Wi-Fi…* 📶", "📡 *Scanning Wi-Fi…* 📶📶", "📡 *Scanning Wi-Fi…* 📶📶📶"],
            )

            import time
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            iface.scan()
            time.sleep(2)
            results = iface.scan_results()

            if not results:
                finish_animation(bot, anim_msg, message.chat.id, "📡 No Wi-Fi networks found nearby.")
                return

            sorted_nets = sorted(results, key=lambda n: n.signal, reverse=True)
            lines = ["```", f"📡  Wi-Fi Scan — {len(sorted_nets)} networks", "─" * 36]
            for net in sorted_nets:
                ssid = (net.ssid or "(hidden)").ljust(28)
                signal = net.signal
                # Signal bar (typically -30 dBm excellent → -90 dBm weak)
                strength = max(0, min(5, round((signal + 90) / 12)))
                bar = "▓" * strength + "░" * (5 - strength)
                lines.append(f"{ssid}  [{bar}] {signal} dBm")
            lines.append("```")
            finish_animation(bot, anim_msg, message.chat.id, "\n".join(lines))

        @bot.message_handler(commands=["clipboard"])
        @auth
        @safe
        def cmd_clipboard(message: object) -> None:
            try:
                import pyperclip
            except ImportError:
                bot.reply_to(message, "❌ pyperclip not installed.\n`pip install pyperclip`", parse_mode="Markdown")
                return

            parts = message.text.split(maxsplit=2)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(
                    message,
                    "📋 *Clipboard usage:*\n`/clipboard get`\n`/clipboard set <text>`",
                    parse_mode="Markdown",
                )
                return

            bot.send_chat_action(message.chat.id, "typing")
            action = parts[1].lower()

            if action == "get":
                content = pyperclip.paste()
                if content:
                    bot.reply_to(message, f"📋 *Clipboard content:*\n```\n{content[:1500]}\n```", parse_mode="Markdown")
                else:
                    bot.reply_to(message, "📋 Clipboard is empty.")
            elif action == "set":
                text = parts[2] if len(parts) > 2 else ""
                pyperclip.copy(text)
                preview = text[:60] + ("…" if len(text) > 60 else "")
                bot.reply_to(message, f"📋 *Clipboard updated:*\n`{preview}`", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Valid actions: `get`, `set`", parse_mode="Markdown")
