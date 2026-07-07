"""
Files module — /getfile, /listdir, /download, /hide, /show, /file
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

import requests

from owlbot.core.utils import format_bytes, safe_unlink, send_large_text
from owlbot.modules.base import BaseModule

_FILE_ATTRIBUTE_HIDDEN = 0x02


class FilesModule(BaseModule):
    name = "files"

    def register(self) -> None:  # noqa: C901 -- flat list of independent handlers, not nested logic
        bot, auth, safe = self.bot, self.auth, self.safe
        cfg = self.config

        @bot.message_handler(commands=["getfile"])
        @auth
        @safe
        def cmd_get_file(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /getfile <path>")
                return
            path = parts[1].strip()
            if not os.path.exists(path):
                bot.reply_to(message, f"❌ Not found: {path}")
                return
            if os.path.isdir(path):
                bot.reply_to(message, "❌ That is a directory. Use /listdir instead.")
                return
            size_mb = os.path.getsize(path) / 1024**2
            if size_mb > cfg.max_file_size_mb:
                bot.reply_to(message, f"❌ File too large ({size_mb:.1f} MB > {cfg.max_file_size_mb} MB).")
                return
            with open(path, "rb") as f:
                bot.send_document(
                    message.chat.id, f,
                    visible_file_name=os.path.basename(path),
                    caption=f"📄 {os.path.basename(path)}  ({size_mb:.2f} MB)",
                )

        @bot.message_handler(commands=["listdir"])
        @auth
        @safe
        def cmd_list_dir(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            path = parts[1].strip() if len(parts) > 1 else os.path.expanduser("~")
            if not os.path.isdir(path):
                bot.reply_to(message, f"❌ Directory not found: {path}")
                return
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                bot.reply_to(message, "❌ Permission denied.")
                return
            if not entries:
                bot.reply_to(message, f"📂 Empty directory: {path}")
                return
            lines = [f"📂 {path}\n"]
            for name in entries:
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    lines.append(f"  📁 {name}/")
                else:
                    try:
                        sz = format_bytes(os.path.getsize(full))
                    except OSError:
                        sz = "?"
                    lines.append(f"  📄 {name}  ({sz})")
            send_large_text(bot, message.chat.id, "\n".join(lines), "directory.txt")

        @bot.message_handler(commands=["download"])
        @auth
        @safe
        def cmd_download(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /download <url>")
                return
            url = parts[1].strip()
            bot.reply_to(message, f"⬇️ Downloading: {url}")
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            size_mb = int(r.headers.get("content-length", 0)) / 1024**2
            if size_mb > cfg.max_download_mb:
                bot.reply_to(message, f"❌ File too large ({size_mb:.1f} MB > {cfg.max_download_mb} MB).")
                return
            filename = url.split("/")[-1].split("?")[0] or "download"
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp:
                for chunk in r.iter_content(8192):
                    tmp.write(chunk)
                tmp_path = tmp.name
            try:
                with open(tmp_path, "rb") as f:
                    bot.send_document(message.chat.id, f, visible_file_name=filename)
            finally:
                safe_unlink(tmp_path)

        @bot.message_handler(commands=["hide"])
        @auth
        @safe
        def cmd_hide(message: object) -> None:
            if sys.platform != "win32":
                bot.reply_to(message, "❌ /hide is Windows-only.")
                return
            import ctypes
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /hide <path>")
                return
            path = parts[1].strip()
            if not os.path.exists(path):
                bot.reply_to(message, f"❌ Not found: {path}")
                return
            ctypes.windll.kernel32.SetFileAttributesW(path, _FILE_ATTRIBUTE_HIDDEN)  # type: ignore[attr-defined]
            bot.reply_to(message, f"👻 Hidden: {path}")

        @bot.message_handler(commands=["show"])
        @auth
        @safe
        def cmd_show(message: object) -> None:
            if sys.platform != "win32":
                bot.reply_to(message, "❌ /show is Windows-only.")
                return
            import ctypes
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /show <path>")
                return
            path = parts[1].strip()
            if not os.path.exists(path):
                bot.reply_to(message, f"❌ Not found: {path}")
                return
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)  # type: ignore[attr-defined]
            ctypes.windll.kernel32.SetFileAttributesW(path, attrs & ~_FILE_ATTRIBUTE_HIDDEN)  # type: ignore[attr-defined]
            bot.reply_to(message, f"👁️ Visible: {path}")

        @bot.message_handler(commands=["file"])
        @auth
        @safe
        def cmd_file(message: object) -> None:
            parts = message.text.split(maxsplit=3)  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(
                    message,
                    "Usage:\n  /file copy <src> <dst>\n  /file move <src> <dst>\n  /file delete <path>",
                )
                return
            action = parts[1].lower()
            if action in ("copy", "move") and len(parts) == 4:
                src, dst = parts[2], parts[3]
                if not os.path.exists(src):
                    bot.reply_to(message, f"❌ Source not found: {src}")
                    return
                if action == "copy":
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    bot.reply_to(message, f"✅ Copied: {src} → {dst}")
                else:
                    shutil.move(src, dst)
                    bot.reply_to(message, f"✅ Moved: {src} → {dst}")
            elif action == "delete" and len(parts) == 3:
                path = parts[2]
                if not os.path.exists(path):
                    bot.reply_to(message, f"❌ Not found: {path}")
                    return
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
                bot.reply_to(message, f"🗑️ Deleted: {path}")
            else:
                bot.reply_to(message, "❌ Invalid usage. See /file for help.")
