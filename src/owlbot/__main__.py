"""
CLI entry point for OwlBot.

Usage:
    owlbot --token YOUR_TOKEN --users 123456789
    owlbot -t YOUR_TOKEN -u 123456789,987654321
"""
from __future__ import annotations

import argparse
import sys


def _ensure_utf8_console() -> None:
    """
    Force UTF-8 output on stdout/stderr.

    Without this, running e.g. ``owlbot --help`` on a default Windows
    console (legacy code page such as cp1252) raises ``UnicodeEncodeError``
    because the CLI text contains emoji. ``errors="replace"`` guarantees we
    never crash even on consoles that truly can't render some glyphs.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, AttributeError):
                pass


def main(argv: list[str] | None = None) -> None:
    _ensure_utf8_console()

    parser = argparse.ArgumentParser(
        prog="owlbot",
        description="🦉 OwlBot — Modular Telegram Windows Remote Control Agent",
    )
    parser.add_argument(
        "-t", "--token",
        required=True,
        help="Telegram bot token (from @BotFather)",
    )
    parser.add_argument(
        "-u", "--users",
        required=True,
        help="Comma-separated list of authorized Telegram user IDs",
    )
    parser.add_argument(
        "--platform",
        default="telegram",
        choices=["telegram"],
        help="Communication platform (default: telegram)",
    )
    parser.add_argument(
        "--modules",
        default=None,
        help=(
            "Comma-separated module names to load. "
            "Defaults to all: system,screen,audio,files,input,processes,monitoring,network,ffmpeg"
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default="owlbot.log",
        help="Path to the log file. Use with --no-log-file to disable it.",
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Do not write any log file to disk (console logging only).",
    )
    parser.add_argument(
        "--disable-logging",
        action="store_true",
        help="Disable logging entirely (no console output, no log file).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + _get_version(),
    )

    args = parser.parse_args(argv)

    # Parse user IDs
    try:
        user_ids = [int(uid.strip()) for uid in args.users.split(",")]
    except ValueError:
        print("Error: --users must be a comma-separated list of integers.", file=sys.stderr)
        sys.exit(1)

    # Parse modules
    modules = None
    if args.modules:
        modules = [m.strip() for m in args.modules.split(",")]

    # Import here to avoid import errors on non-Windows when just --help
    from owlbot import OwlBot

    log_file = None if args.no_log_file else args.log_file

    bot = OwlBot(
        token=args.token,
        authorized_users=user_ids,
        platform=args.platform,
        modules=modules,
        log_level=args.log_level,
        log_file=log_file,
        enable_logging=not args.disable_logging,
    )
    bot.run()


def _get_version() -> str:
    try:
        from owlbot import __version__
        return __version__
    except ImportError:
        return "unknown"


if __name__ == "__main__":
    main()
