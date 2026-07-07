"""
OwlBot — Main Public API
"""
from __future__ import annotations

import logging
import sys
from typing import List, Optional

from owlbot.config import AVAILABLE_MODULES, BotConfig
from owlbot.platform.telegram import TelegramPlatform


logger = logging.getLogger("owlbot")


def _configure_logging(config: BotConfig) -> None:
    """
    Configure (or intentionally disable) logging for the whole ``owlbot``
    logger hierarchy, based on ``config.enable_logging`` / ``config.log_file``.

    - ``enable_logging=False`` → no handlers at all, logger is silenced.
    - ``log_file`` falsy (``None`` / ``""``) → console-only logging, no
      log file is created on disk.
    - Otherwise → console + rotating-free file logging, as before.
    """
    root_owlbot_logger = logging.getLogger("owlbot")
    root_owlbot_logger.handlers.clear()

    if not config.enable_logging:
        root_owlbot_logger.addHandler(logging.NullHandler())
        root_owlbot_logger.propagate = False
        return

    root_owlbot_logger.propagate = False
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    root_owlbot_logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Force UTF-8 on stdout so emoji in future log messages never crash on
    # a legacy Windows console code page (e.g. cp1252).
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, AttributeError):
            pass

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_owlbot_logger.addHandler(stream_handler)

    if config.log_file:
        file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_owlbot_logger.addHandler(file_handler)


class OwlBot:
    """
    Main class for users — clean and simple API.

    Usage::

        from owlbot import OwlBot

        bot = OwlBot(
            token="YOUR_BOT_TOKEN",
            authorized_users=[123456789],
            modules=["system", "screen", "audio"],
        )
        bot.run()
    """

    def __init__(
        self,
        token: str,
        authorized_users: List[int],
        platform: str = "telegram",
        modules: Optional[List[str]] = None,
        log_level: str = "INFO",
        log_file: Optional[str] = "owlbot.log",
        enable_logging: bool = True,
        **kwargs: object,
    ) -> None:
        self.config = BotConfig(
            token=token,
            authorized_users=authorized_users,
            platform=platform,
            modules=modules or list(AVAILABLE_MODULES),
            log_level=log_level,
            log_file=log_file,
            enable_logging=enable_logging,
            **kwargs,
        )

        _configure_logging(self.config)

        from owlbot import __version__ as _owlbot_version

        logger.info("Initializing OwlBot v%s with platform: %s", _owlbot_version, platform)

        # Platform Adapter (Telegram for now)
        if platform == "telegram":
            self._platform = TelegramPlatform(self.config)
        else:
            raise NotImplementedError(f"Platform '{platform}' not supported yet.")

        logger.info("OwlBot initialized successfully.")

    def run(self) -> None:
        """Start the bot."""
        try:
            for uid in self.config.authorized_users:
                try:
                    if hasattr(self._platform, "_bot"):
                        self._platform._bot.send_message(
                            uid,
                            "🟢 **Owl Bot is online!**\n\nType `/help` for commands.",
                            parse_mode="Markdown",
                        )
                except Exception:
                    logger.warning(
                        "Could not send startup notification to user %s", uid, exc_info=True
                    )

            self._platform.run()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception:
            logger.critical("Bot crashed", exc_info=True)
        finally:
            logger.info("OwlBot shutdown complete.")


__all__ = ["OwlBot"]
