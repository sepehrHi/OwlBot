"""
Audio module — /mute, /unmute, /volume, /startrec, /stoprec, /playvoice
Windows-only module (requires pyaudio, pycaw).
All non-stdlib imports are lazy inside handlers.

Bug-fix v1.1: wav_path is now cleaned up after voice playback.
"""
from __future__ import annotations

import os
import tempfile
import threading
import time
import wave

from owlbot.core.utils import animate_message, finish_animation, safe_unlink
from owlbot.modules.base import BaseModule


class AudioModule(BaseModule):
    name = "audio"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._recording = False
        self._frames: list[bytes] = []
        self._lock = threading.Lock()
        self._play_voice_mode = False
        self._pyaudio_mod = None
        self._pa = None
        self._pending_msg: dict = {}

    def _get_pa(self):
        """Lazy-init PyAudio on first use."""
        if self._pa is None:
            import pyaudio
            self._pyaudio_mod = pyaudio
            self._FORMAT = pyaudio.paInt16
            self._pa = pyaudio.PyAudio()
        return self._pa, self._FORMAT

    def register(self) -> None:  # noqa: C901
        bot, auth, safe = self.bot, self.auth, self.safe
        cfg = self.config

        @bot.message_handler(commands=["mute"])
        @auth
        @safe
        def cmd_mute(message: object) -> None:
            import pyautogui
            pyautogui.press("volumemute")
            bot.reply_to(message, "🔇 *Audio muted.*", parse_mode="Markdown")

        @bot.message_handler(commands=["unmute"])
        @auth
        @safe
        def cmd_unmute(message: object) -> None:
            import pyautogui
            pyautogui.press("volumemute")
            bot.reply_to(message, "🔊 *Audio unmuted.*", parse_mode="Markdown")

        @bot.message_handler(commands=["volume"])
        @auth
        @safe
        def cmd_volume(message: object) -> None:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            parts = message.text.split()  # type: ignore[attr-defined]
            if len(parts) < 2:
                bot.reply_to(message, "📢 Usage: `/volume <0-100>`", parse_mode="Markdown")
                return
            try:
                level = int(parts[1])
            except ValueError:
                bot.reply_to(message, "❌ Volume must be an integer 0–100.")
                return
            if not 0 <= level <= 100:
                bot.reply_to(message, "❌ Volume must be between 0 and 100.")
                return
            bot.send_chat_action(message.chat.id, "typing")
            changed = 0
            for session in AudioUtilities.GetAllSessions():
                try:
                    vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                    vol.SetMasterVolume(level / 100.0, None)
                    changed += 1
                except Exception:
                    pass
            if changed:
                bot.reply_to(message, f"🔊 *Volume set to {level}%* ({changed} session(s)).", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ No active audio sessions found.")

        @bot.message_handler(commands=["startrec"])
        @auth
        @safe
        def cmd_start_rec(message: object) -> None:
            if self._recording:
                bot.reply_to(message, "⚠️ Already recording. Use /stoprec to stop.")
                return
            parts = message.text.split()  # type: ignore[attr-defined]
            try:
                duration = int(parts[1]) if len(parts) > 1 else 5
            except ValueError:
                bot.reply_to(message, "❌ Duration must be an integer.")
                return
            if not cfg.min_record_duration <= duration <= cfg.max_record_duration:
                bot.reply_to(
                    message,
                    f"❌ Duration must be {cfg.min_record_duration}–{cfg.max_record_duration}s.",
                )
                return
            self._recording = True
            threading.Thread(target=self._record_worker, args=(duration,), daemon=True).start()
            bot.send_chat_action(message.chat.id, "record_audio")
            anim_msg = animate_message(
                bot, message.chat.id,
                [f"🎙️ *Recording for {duration}s…* 🔴", f"🎙️ *Recording for {duration}s…* 🔴⚫"],
            )
            self._pending_msg[message.chat.id] = anim_msg

            def _auto_send() -> None:
                time.sleep(duration + 1.5)
                if self._recording:
                    self._recording = False
                    self._send_recording(message.chat.id)

            threading.Thread(target=_auto_send, daemon=True).start()

        @bot.message_handler(commands=["stoprec"])
        @auth
        @safe
        def cmd_stop_rec(message: object) -> None:
            if not self._recording:
                bot.reply_to(message, "⚠️ No active recording.")
                return
            self._recording = False
            time.sleep(0.5)
            bot.send_chat_action(message.chat.id, "upload_voice")
            self._send_recording(message.chat.id)

        @bot.message_handler(commands=["playvoice"])
        @auth
        @safe
        def cmd_play_voice(message: object) -> None:
            self._play_voice_mode = not self._play_voice_mode
            state = "enabled ✅" if self._play_voice_mode else "disabled ❌"
            bot.reply_to(message, f"🔊 *Direct voice playback* {state}.", parse_mode="Markdown")

        @bot.message_handler(content_types=["voice"])
        def handle_voice(message: object) -> None:
            if message.chat.id not in self.config.authorized_users:  # type: ignore[attr-defined]
                return
            if not self._play_voice_mode:
                return
            self._play_incoming_voice(message)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _record_worker(self, duration_sec: int) -> None:
        pa, fmt = self._get_pa()
        cfg = self.config
        stream = pa.open(
            format=fmt, channels=cfg.audio_channels, rate=cfg.audio_sample_rate,
            input=True, frames_per_buffer=cfg.audio_chunk_size,
        )
        try:
            with self._lock:
                self._frames.clear()
            deadline = time.time() + duration_sec
            while self._recording and time.time() < deadline:
                data = stream.read(cfg.audio_chunk_size, exception_on_overflow=False)
                with self._lock:
                    self._frames.append(data)
        finally:
            stream.stop_stream()
            stream.close()
            self._recording = False

    def _save_wav(self, path: str) -> None:
        pa, fmt = self._get_pa()
        cfg = self.config
        with wave.open(path, "wb") as wf:
            wf.setnchannels(cfg.audio_channels)
            wf.setsampwidth(pa.get_sample_size(fmt))
            wf.setframerate(cfg.audio_sample_rate)
            with self._lock:
                wf.writeframes(b"".join(self._frames))

    def _send_recording(self, chat_id: int) -> None:
        anim_msg = self._pending_msg.pop(chat_id, None)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name
        try:
            self._save_wav(tmp_path)
            finish_animation(self.bot, anim_msg, chat_id, "✅ *Recording ready — sending…*")
            with open(tmp_path, "rb") as f:
                self.bot.send_voice(chat_id, f)
            self.bot.send_message(chat_id, "✅ *Recording sent.*", parse_mode="Markdown")
        except Exception as exc:
            self.bot.send_message(chat_id, f"❌ Failed to send recording: {exc}")
        finally:
            safe_unlink(tmp_path)

    def _play_incoming_voice(self, message: object) -> None:
        bot = self.bot
        file_info = bot.get_file(message.voice.file_id)  # type: ignore[attr-defined]
        downloaded = bot.download_file(file_info.file_path)
        ogg_path = ""
        wav_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
                ogg_path = f.name
            wav_path = ogg_path + ".wav"
            with open(ogg_path, "wb") as f:
                f.write(downloaded)
            ret = os.system(f'ffmpeg -y -i "{ogg_path}" "{wav_path}" -loglevel quiet')
            if ret != 0:
                bot.reply_to(message, "❌ ffmpeg conversion failed. Is ffmpeg installed? Try /ffmpeg")
                return
            bot.send_chat_action(message.chat.id, "record_audio")
            threading.Thread(target=self._play_wav, args=(wav_path,), daemon=True).start()
            bot.reply_to(message, "🔊 *Playing voice message…*", parse_mode="Markdown")
        except Exception as exc:
            bot.reply_to(message, f"❌ Voice playback error: {exc}")
            safe_unlink(wav_path)
        finally:
            safe_unlink(ogg_path)
        # Note: wav_path is cleaned up inside _play_wav after playback finishes

    def _play_wav(self, filepath: str) -> None:
        pa, fmt = self._get_pa()
        cfg = self.config
        try:
            with wave.open(filepath, "rb") as wf:
                stream = pa.open(
                    format=pa.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(), rate=wf.getframerate(), output=True,
                )
                try:
                    chunk = wf.readframes(cfg.audio_chunk_size)
                    while chunk:
                        stream.write(chunk)
                        chunk = wf.readframes(cfg.audio_chunk_size)
                finally:
                    stream.stop_stream()
                    stream.close()
        finally:
            safe_unlink(filepath)  # ✅ Bug-fix: always clean up the wav temp file
