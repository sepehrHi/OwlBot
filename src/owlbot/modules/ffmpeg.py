"""
FFmpeg module — /ffmpeg, /ffmpeg_install
Check FFmpeg status and download/install it automatically on Windows.

Public API (importable by user scripts):
    check_ffmpeg()           -> (bool, str)
    download_ffmpeg(add_to_path=True) -> (bool, str)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import zipfile

from owlbot.core.utils import animate_message, finish_animation
from owlbot.modules.base import BaseModule

# Official Gyan.dev release build — widely used, reliable, GPL static build
_FFMPEG_WIN_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


# ── Public helpers ────────────────────────────────────────────────────────────

def check_ffmpeg() -> tuple[bool, str]:
    """
    Return ``(available, detail_string)``.

    *detail_string* contains version + path on success, or an explanation
    when FFmpeg is absent or broken.
    """
    path = shutil.which("ffmpeg")
    if not path:
        return False, "FFmpeg not found in PATH."
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=5,
        )
        first_line = (result.stdout or "").splitlines()[0] or "unknown version"
        return True, f"{first_line}\n📍 {path}"
    except Exception as exc:
        return True, f"Found at {path} — version check failed: {exc}"


def _download_with_retry(
    url: str, dst_path: str, max_mb: int = 200, max_attempts: int = 3,
    progress_callback: object | None = None,
) -> tuple[bool, str]:
    """
    Download a file with progress reports, MB progress bars, retries, and exponential backoff.

    Parameters
    ----------
    url : str
        Remote URL to fetch.
    dst_path : str
        Local path to save the downloaded file.
    max_mb : int, optional
        Maximum expected file size in megabytes. Used for progress bar sizing, by default 200.
    max_attempts : int, optional
        Number of retry attempts on network errors, by default 3.
    progress_callback : callable or None, optional
        If given, called as ``progress_callback(current_mb, total_mb)`` after
        every 5 MB downloaded. Useful for updating a Telegram message.

    Returns
    -------
    tuple[bool, str]
        ``(success, message)`` where ``success`` is ``True`` on a successful download,
        ``False`` otherwise. ``message`` contains details of result or error description.
    """
    import urllib.request
    import time

    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                                       "Chrome/115.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=60) as r, open(dst_path, "wb") as out:
                total = int(r.headers.get("Content-Length", 0))

                if total <= 0:
                    print("   ⬇️  Downloading (size unknown)…")
                    shutil.copyfileobj(r, out)
                    print("   ✅ Download complete (size unknown).\n")
                    return True, "Download finished."

                # Track progress
                downloaded = 0
                last_mb_reported = -1
                chunk = 65536
                started = time.time()

                while True:
                    data = r.read(chunk)
                    if not data:
                        break
                    out.write(data)
                    downloaded += len(data)

                    current_mb = downloaded // (1024 * 1024)
                    if current_mb > last_mb_reported:
                        last_mb_reported = current_mb
                        total_mb = total // (1024 * 1024)
                        # Terminal progress line
                        bar_len = 20
                        filled = min(int((current_mb / max_mb) * bar_len), bar_len)
                        bar = "█" * filled + "░" * (bar_len - filled)
                        elapsed = time.time() - started
                        rate = downloaded / (elapsed or 0.001)
                        eta = (total - downloaded) / rate if rate > 1 else 0
                        print(
                            f"   ⬇️  {current_mb:>5} MB / {total_mb} MB "
                            f"[{bar}]  {int(eta)}s ETA"
                        )
                        # Telegram callback
                        if progress_callback:
                            progress_callback(current_mb, total_mb)

                # Final report
                total_mb = total // (1024 * 1024)
                bar_len = 20
                filled = min(int((total_mb / max_mb) * bar_len), bar_len)
                bar = "█" * filled + "░" * (bar_len - filled)
                print(f"   ✅ {total_mb:>5} MB / {total_mb} MB [{bar}] — DONE\n")
                if progress_callback:
                    progress_callback(total_mb, total_mb)
                return True, "Download complete."

        except Exception as exc:
            if attempt == max_attempts:
                return False, f"Download failed after {max_attempts} attempts: {exc}"
            sleep_time = min(2 ** attempt, 16)  # cap at 16s
            print(f"   ⏳ Retry {attempt}/{max_attempts} in {sleep_time}s…")
            time.sleep(sleep_time)

    return False, "Download failed unexpectedly"


def download_ffmpeg(
    add_to_path: bool = True,
    progress_callback: object | None = None,
) -> tuple[bool, str]:
    """
    Download FFmpeg for Windows and optionally add it to the user PATH.

    Parameters
    ----------
    add_to_path:
        ``True``  — install to ``%LOCALAPPDATA%\\OwlBot\\ffmpeg`` and
                    permanently add the bin dir to HKCU\\Environment PATH.
        ``False`` — extract to a temp dir; PATH is *not* modified.
    progress_callback:
        If given, forwarded to ``_download_with_retry`` for per-MB progress.

    Returns
    -------
    ``(success: bool, message: str)``
    """
    if sys.platform != "win32":
        return False, "Automatic FFmpeg download is Windows-only."

    install_dir = (
        os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "OwlBot", "ffmpeg")
        if add_to_path
        else os.path.join(tempfile.gettempdir(), "owlbot_ffmpeg")
    )
    os.makedirs(install_dir, exist_ok=True)
    zip_path = os.path.join(install_dir, "ffmpeg.zip")

    success, err_msg = _download_with_retry(
        _FFMPEG_WIN_URL, zip_path, progress_callback=progress_callback,
    )
    if not success:
        return False, err_msg

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(install_dir)
    except Exception as exc:
        return False, f"Extraction failed: {exc}"
    finally:
        try:
            os.unlink(zip_path)
        except OSError:
            pass

    # Locate ffmpeg.exe inside the extracted directory tree
    bin_dir: str | None = None
    for root, _dirs, files in os.walk(install_dir):
        if "ffmpeg.exe" in files:
            bin_dir = root
            break

    if bin_dir is None:
        return False, "Could not locate ffmpeg.exe after extraction."

    if add_to_path:
        try:
            import winreg  # type: ignore[import]
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment", 0, winreg.KEY_ALL_ACCESS,
            )
            current = winreg.QueryValueEx(key, "PATH")[0]
            if bin_dir not in current:
                winreg.SetValueEx(
                    key, "PATH", 0, winreg.REG_EXPAND_SZ, current + ";" + bin_dir,
                )
            winreg.CloseKey(key)
        except Exception as exc:
            return False, f"Extracted to {bin_dir} but PATH update failed: {exc}"
        # Apply immediately to current process
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + bin_dir
        return True, (
            f"✅ FFmpeg installed to:\n`{bin_dir}`\n\n"
            "Added to user PATH.\n"
            "_Restart your terminal or PC for PATH to take effect everywhere._"
        )

    return True, f"✅ FFmpeg downloaded to:\n`{bin_dir}`\n_(PATH was not modified)_"


# ── Telegram module ───────────────────────────────────────────────────────────

class FFmpegModule(BaseModule):
    """Telegram command handlers for FFmpeg status checking & installation."""

    name = "ffmpeg"

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["ffmpeg"])
        @auth
        @safe
        def cmd_ffmpeg_status(message: object) -> None:
            bot.send_chat_action(message.chat.id, "typing")
            available, detail = check_ffmpeg()
            if available:
                text = f"✅ *FFmpeg is available*\n\n```\n{detail}\n```"
            else:
                text = (
                    "❌ *FFmpeg not found*\n\n"
                    f"{detail}\n\n"
                    "Run /ffmpeg\\_install to download and set it up automatically."
                )
            bot.reply_to(message, text, parse_mode="Markdown")

        @bot.message_handler(commands=["ffmpeg_install"])
        @auth
        @safe
        def cmd_ffmpeg_install(message: object) -> None:
            if sys.platform != "win32":
                bot.reply_to(message, "❌ `/ffmpeg_install` is Windows-only.", parse_mode="Markdown")
                return

            # Don't re-install if already present
            available, detail = check_ffmpeg()
            if available:
                bot.reply_to(
                    message,
                    f"✅ *FFmpeg is already installed!*\n\n```\n{detail}\n```",
                    parse_mode="Markdown",
                )
                return

            parts = message.text.split()  # type: ignore[attr-defined]
            add_to_path = not (len(parts) > 1 and parts[1].lower() in ("false", "0", "no"))

            bot.send_chat_action(message.chat.id, "upload_document")
            # Initial animation frames (show while waiting for content-length)
            anim_msg = animate_message(
                bot, message.chat.id,
                ["⬇️ *Downloading FFmpeg…* ⏳", "⬇️ *Downloading FFmpeg…* ⏳⏳", "⬇️ *Downloading FFmpeg…* ⏳⏳⏳"],
                delay=0.8,
            )

            # Progress callback: update the Telegram message with MB progress
            def _progress(current_mb: int, total_mb: int) -> None:
                try:
                    pct = min(int(current_mb / max(total_mb, 1) * 100), 100)
                    bar_len = 16
                    filled = int(pct / 100 * bar_len)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    text = (
                        f"⬇️ *Downloading FFmpeg…*\n"
                        f"`{bar}`  {current_mb} MB / {total_mb} MB  ({pct}%)"
                    )
                    bot.edit_message_text(
                        text, chat_id=message.chat.id,
                        message_id=anim_msg.message_id,
                        parse_mode="Markdown",
                    )
                except Exception:
                    pass  # best-effort

            def _worker() -> None:
                success, msg = download_ffmpeg(
                    add_to_path=add_to_path, progress_callback=_progress,
                )
                icon = "🎬" if success else "❌"
                finish_animation(bot, anim_msg, message.chat.id, f"{icon} {msg}")

            threading.Thread(target=_worker, daemon=True).start()


__all__ = ["FFmpegModule", "check_ffmpeg", "download_ffmpeg"]
