"""
Telegram platform adapter — wraps TeleBot and wires modules.
"""
from __future__ import annotations

import logging
from typing import List

from telebot import TeleBot

from owlbot.config import BotConfig
from owlbot.core.decorators import make_authorized_only, make_safe_reply
from owlbot.modules import MODULE_REGISTRY

logger = logging.getLogger("owlbot.platform.telegram")


class TelegramPlatform:
    """
    Builds a TeleBot instance, instantiates requested modules,
    calls .register() on each, and exposes .run().
    """

    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self._bot = TeleBot(config.token, parse_mode=None)
        auth = make_authorized_only(config.authorized_users, self._bot)
        safe = make_safe_reply(self._bot)
        self._modules = []

        for name in config.modules:
            cls = MODULE_REGISTRY.get(name)
            if cls is None:
                logger.warning("Module '%s' not found in registry — skipping.", name)
                continue
            mod = cls(config=config, bot=self._bot, auth=auth, safe=safe)
            mod.register()
            self._modules.append(mod)
            logger.info("Module registered: %s", name)

    def run(self) -> None:
        logger.info("Starting Telegram bot (polling)…")
        try:
            self._bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=15)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.error("Bot crashed", exc_info=True)