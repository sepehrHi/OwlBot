"""
OwlBot — Main Public API
"""
from __future__ import annotations

import logging
import sys
from typing import List, Optional

from owlbot.config import BotConfig
from owlbot.platform.telegram import TelegramPlatform


logger = logging.getLogger("owlbot")


class OwlBot:
    """
    Main class for users — clean and simple API.
    """

    def __init__(
        self,
        token: str,
        authorized_users: List[int],
        platform: str = "telegram",
        modules: Optional[List[str]] = None,
        log_level: str = "INFO",
        log_file: str = "owlbot.log",
        **kwargs
    ):
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file, encoding="utf-8"),
            ],
            force=True,
        )

        self.config = BotConfig(
            token=token,
            authorized_users=authorized_users,
            platform=platform,
            modules=modules or ["system", "screen", "audio", "files", "input", "processes", "monitoring", "network"],
            log_level=log_level,
            log_file=log_file,
            **kwargs
        )

        logger.info(f"Initializing OwlBot v1.0.0 with platform: {platform}")

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
                    if hasattr(self._platform, '_bot'):
                        self._platform._bot.send_message(
                            uid,
                            "🟢 **Owl Bot is online!**\n\nType `/help` for commands.",
                            parse_mode="Markdown"
                        )
                except:
                    pass

            self._platform.run()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.critical("Bot crashed", exc_info=True)
        finally:
            logger.info("OwlBot shutdown complete.")


__all__ = ["OwlBot"]