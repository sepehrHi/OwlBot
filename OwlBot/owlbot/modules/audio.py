"""
Audio module — /mute, /unmute, /volume, /startrec, /stoprec, /playvoice
"""
from __future__ import annotations

import os
import tempfile
import threading
import time
import wave

import pyaudio
import pyautogui
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

from owlbot.core.utils import safe_unlink
from owlbot.modules.base import BaseModule

_FORMAT = pyaudio.paInt16


class AudioModule(BaseModule):
    name = "audio"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pa = pyaudio.PyAudio()
        self._recording = False
        self._frames: list[bytes] = []
        self._lock = threading.Lock()
        self._play_voice_mode = False

    # ── Public interface ────────────────────────────────────────────────────

    def register(self) -> None:
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["mute"])
        @auth
        @safe
        def cmd_mute(message):
            pyautogui.press("volumemute")
            bot.reply_to(message, "🔇 Audio muted.")

        @bot.message_handler(commands=["unmute"])
        @auth
        @safe
        def cmd_unmute(message):
            pyautogui.press("volumemute")
            bot.reply_to(message, "🔊 Audio unmuted.")

        @bot.message_handler(commands=["volume"])
        @auth
        @safe
        def cmd_volume(message):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /volume <0-100>")
                return
            try:
                level = int(parts[1])
            except ValueError:
                bot.reply_to(message, "❌ Volume must be an integer 0–100.")
                return
            if not 0 <= level <= 100:
                bot.reply_to(message, "❌ Volume must be between 0 and 100.")
                return
            changed = 0
            for session in AudioUtilities.GetAllSessions():
                try:
                    vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                    vol.SetMasterVolume(level / 100.0, None)
                    changed += 1
                except Exception:
                    pass
            if changed:
                bot.reply_to(message, f"🔊 Volume set to {level}% ({changed} session(s)).")
            else:
                bot.reply_to(message, "❌ No active audio sessions found.")

        @bot.message_handler(commands=["startrec"])
        @auth
        @safe
        def cmd_start_rec(message):
            if self._recording:
                bot.reply_to(message, "⚠️ Already recording. Use /stoprec to stop.")
                return
            parts = message.text.split()
            try:
                duration = int(parts[1]) if len(parts) > 1 else 5
            except ValueError:
                bot.reply_to(message, "❌ Duration must be an integer.")
                return
            cfg = self.config
            if not cfg.min_record_duration <= duration <= cfg.max_record_duration:
                bot.reply_to(
                    message,
                    f"❌ Duration must be {cfg.min_record_duration}–{cfg.max_record_duration}s.",
                )
                return
            self._recording = True
            threading.Thread(
                target=self._record_worker, args=(duration,), daemon=True
            ).start()
            bot.reply_to(message, f"🎙️ Recording for {duration}s — use /stoprec to stop early.")

            def _auto_send():
                time.sleep(duration + 1.5)
                if self._recording:
                    self._recording = False
                    self._send_recording(message.chat.id)

            threading.Thread(target=_auto_send, daemon=True).start()

        @bot.message_handler(commands=["stoprec"])
        @auth
        @safe
        def cmd_stop_rec(message):
            if not self._recording:
                bot.reply_to(message, "⚠️ No active recording.")
                return
            self._recording = False
            time.sleep(0.5)
            self._send_recording(message.chat.id)

        @bot.message_handler(commands=["playvoice"])
        @auth
        @safe
        def cmd_play_voice(message):
            self._play_voice_mode = not self._play_voice_mode
            state = "enabled ✅" if self._play_voice_mode else "disabled ❌"
            bot.reply_to(message, f"🔊 Direct voice playback {state}.")

        @bot.message_handler(content_types=["voice"])
        def handle_voice(message):
            if message.chat.id not in self.config.authorized_users:
                return
            if not self._play_voice_mode:
                return
            self._play_incoming_voice(message)

    # ── Private helpers ─────────────────────────────────────────────────────

    def _record_worker(self, duration_sec: int) -> None:
        cfg = self.config
        stream = self._pa.open(
            format=_FORMAT,
            channels=cfg.audio_channels,
            rate=cfg.audio_sample_rate,
            input=True,
            frames_per_buffer=cfg.audio_chunk_size,
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
        cfg = self.config
        with wave.open(path, "wb") as wf:
            wf.setnchannels(cfg.audio_channels)
            wf.setsampwidth(self._pa.get_sample_size(_FORMAT))
            wf.setframerate(cfg.audio_sample_rate)
            with self._lock:
                wf.writeframes(b"".join(self._frames))

    def _send_recording(self, chat_id: int) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name
        try:
            self._save_wav(tmp_path)
            with open(tmp_path, "rb") as f:
                self.bot.send_voice(chat_id, f)
            self.bot.send_message(chat_id, "✅ Recording sent.")
        except Exception as exc:
            self.bot.send_message(chat_id, f"❌ Failed to send recording: {exc}")
        finally:
            safe_unlink(tmp_path)

    def _play_incoming_voice(self, message) -> None:
        bot = self.bot
        file_info = bot.get_file(message.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
            ogg_path = f.name
        wav_path = ogg_path + ".wav"
        try:
            with open(ogg_path, "wb") as f:
                f.write(downloaded)
            ret = os.system(f'ffmpeg -y -i "{ogg_path}" "{wav_path}" -loglevel quiet')
            if ret != 0:
                bot.reply_to(message, "❌ ffmpeg conversion failed.")
                return
            threading.Thread(
                target=self._play_wav, args=(wav_path,), daemon=True
            ).start()
            bot.reply_to(message, "🔊 Playing voice message...")
        except Exception as exc:
            bot.reply_to(message, f"❌ Voice playback error: {exc}")
        finally:
            safe_unlink(ogg_path)

    def _play_wav(self, filepath: str) -> None:
        cfg = self.config
        with wave.open(filepath, "rb") as wf:
            stream = self._pa.open(
                format=self._pa.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )
            try:
                chunk = wf.readframes(cfg.audio_chunk_size)
                while chunk:
                    stream.write(chunk)
                    chunk = wf.readframes(cfg.audio_chunk_size)
            finally:
                stream.stop_stream()
                stream.close()
        safe_unlink(filepath)
