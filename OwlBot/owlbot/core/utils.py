"""
Shared utility helpers used across all modules.
"""
from __future__ import annotations

import logging
import os
import tempfile

logger = logging.getLogger("owlbot.utils")


def send_large_text(bot, chat_id: int, text: str, filename: str = "output.txt") -> None:
    """Send text as a message (≤4 000 chars) or as a .txt document."""
    if len(text) <= 4_000:
        bot.send_message(chat_id, text)
    else:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(text)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                bot.send_document(chat_id, f, visible_file_name=filename)
        finally:
            safe_unlink(tmp_path)


def safe_unlink(path: str) -> None:
    """Delete a file silently if it exists."""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except Exception as exc:
        logger.warning("Could not delete temp file %s: %s", path, exc)


def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1_024:
            return f"{n:.2f} {unit}"
        n /= 1_024
    return f"{n:.2f} PB"


def format_uptime(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3_600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"
