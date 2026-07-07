"""
Network module — /wifiscan, /clipboard
Cross-platform module with lazy imports.
"""
from __future__ import annotations

import sys

from owlbot.modules.base import BaseModule


class NetworkModule(BaseModule):
    name = "network"

    def register(self) -> None:  # noqa: C901 -- flat list of independent handlers, not nested logic
        bot, auth, safe = self.bot, self.auth, self.safe

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
                bot.reply_to(message, "❌ pywifi not installed.")
                return
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            iface.scan()
            import time
            time.sleep(2)
            results = iface.scan_results()
            if not results:
                bot.reply_to(message, "📡 No Wi-Fi networks found.")
                return
            lines = ["📡 Wi-Fi Networks:\n"]
            for net in sorted(results, key=lambda n: n.signal, reverse=True):
                ssid = net.ssid or "(hidden)"
                lines.append(f"  {ssid:<30}  signal: {net.signal} dBm")
            bot.reply_to(message, "\n".join(lines))

        @bot.message_handler(commands=["clipboard"])
        @auth
        @safe
        def cmd_clipboard(message: object) -> None:
            try:
                import pyperclip
            except ImportError:
                bot.reply_to(message, "❌ pyperclip not installed.")
                return
            parts = message.text.split(maxsplit=2)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage:\n  /clipboard get\n  /clipboard set <text>")
                return
            action = parts[1].lower()
            if action == "get":
                content = pyperclip.paste()
                bot.reply_to(
                    message,
                    f"📋 Clipboard:\n{content}" if content else "📋 Clipboard is empty.",
                )
            elif action == "set":
                text = parts[2] if len(parts) > 2 else ""
                pyperclip.copy(text)
                bot.reply_to(message, f"📋 Clipboard updated: {text[:60]}")
            else:
                bot.reply_to(message, "❌ Valid actions: get, set")
