"""
Input module — /type, /move, /mouse, /hotkey, /msg, /mousepos
Windows-only module (requires keyboard, pyautogui).
All heavy imports are lazy inside handlers.
"""
from __future__ import annotations

from owlbot.modules.base import BaseModule


class InputModule(BaseModule):
    name = "input"

    def register(self) -> None:  # noqa: C901 -- flat list of independent handlers, not nested logic
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["type"])
        @auth
        @safe
        def cmd_type(message: object) -> None:
            import keyboard
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /type <text>")
                return
            keyboard.write(parts[1])
            preview = parts[1][:60] + ("..." if len(parts[1]) > 60 else "")
            bot.reply_to(message, f"⌨️ Typed: {preview}")

        @bot.message_handler(commands=["move"])
        @auth
        @safe
        def cmd_move(message: object) -> None:
            import pyautogui
            parts = message.text.split()  # type: ignore[attr-defined]
            if len(parts) < 3:
                bot.reply_to(message, "Usage: /move <x> <y>")
                return
            try:
                x, y = int(parts[1]), int(parts[2])
            except ValueError:
                bot.reply_to(message, "❌ Coordinates must be integers.")
                return
            pyautogui.moveTo(x, y, duration=0.3)
            bot.reply_to(message, f"🖱️ Mouse moved to ({x}, {y}).")

        @bot.message_handler(commands=["mousepos"])
        @auth
        @safe
        def cmd_mousepos(message: object) -> None:
            import pyautogui
            x, y = pyautogui.position()
            bot.reply_to(message, f"🖱️ Current mouse position: ({x}, {y})")

        @bot.message_handler(commands=["mouse"])
        @auth
        @safe
        def cmd_mouse(message: object) -> None:
            import pyautogui
            parts = message.text.split(maxsplit=2)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(
                    message,
                    "Usage:\n  /mouse click [left|right|middle]\n"
                    "  /mouse scroll <n>\n  /mouse drag <x>,<y>",
                )
                return
            action = parts[1].lower()
            if action == "click":
                btn = parts[2].lower() if len(parts) > 2 else "left"
                if btn not in ("left", "right", "middle"):
                    bot.reply_to(message, "❌ Valid buttons: left, right, middle")
                    return
                pyautogui.click(button=btn)
                bot.reply_to(message, f"🖱️ {btn.capitalize()} click.")
            elif action == "scroll":
                try:
                    amount = int(parts[2]) if len(parts) > 2 else 3
                except ValueError:
                    bot.reply_to(message, "❌ Scroll amount must be an integer.")
                    return
                pyautogui.scroll(amount)
                bot.reply_to(message, f"🖱️ Scrolled {amount} units.")
            elif action == "drag":
                if len(parts) < 3:
                    bot.reply_to(message, "Usage: /mouse drag <x>,<y>")
                    return
                try:
                    x, y = map(int, parts[2].split(","))
                except ValueError:
                    bot.reply_to(message, "❌ Format: /mouse drag x,y")
                    return
                pyautogui.dragTo(x, y, duration=0.5)
                bot.reply_to(message, f"🖱️ Dragged to ({x}, {y}).")
            else:
                bot.reply_to(message, "❌ Valid actions: click, scroll, drag")

        @bot.message_handler(commands=["hotkey"])
        @auth
        @safe
        def cmd_hotkey(message: object) -> None:
            import pyautogui
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /hotkey <key+key+...>  e.g. /hotkey ctrl+c")
                return
            keys = [k.strip() for k in parts[1].lower().split("+")]
            pyautogui.hotkey(*keys)
            bot.reply_to(message, f"⌨️ Hotkey: {'+'.join(keys)}")

        @bot.message_handler(commands=["msg"])
        @auth
        @safe
        def cmd_msg(message: object) -> None:
            import ctypes
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /msg <text>")
                return
            ctypes.windll.user32.MessageBoxW(0, parts[1], "Owl Bot", 0x40)  # type: ignore[attr-defined]
            bot.reply_to(message, f"📢 Message box displayed: {parts[1][:60]}")
