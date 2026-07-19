"""
owlbot/core/help.py
Dynamic help builder — generates context-aware Markdown help text
based on which modules are currently loaded in the bot instance.
"""
from __future__ import annotations

# (title, command-list) per module name
_MODULE_HELP: dict[str, tuple[str, str]] = {
    "system": (
        "🖥️  System",
        "/status    — CPU · RAM · disk · battery\n"
        "/uptime    — System uptime\n"
        "/ping      — Ping the bot\n"
        "/lock      — Lock workstation\n"
        "/shutdown  — Shut down PC\n"
        "/restart   — Restart PC",
    ),
    "screen": (
        "📸  Screen",
        "/screenshot           — Capture screen\n"
        "/webcam               — Webcam snapshot\n"
        "/timelapse <ivl> <n>  — Auto screenshots\n"
        "/startstream          — Start screen stream\n"
        "/stopstream           — Stop stream",
    ),
    "audio": (
        "🔊  Audio",
        "/mute              — Mute audio\n"
        "/unmute            — Unmute audio\n"
        "/volume <0-100>    — Set volume\n"
        "/startrec [sec]    — Record microphone\n"
        "/stoprec           — Stop & send recording\n"
        "/playvoice         — Toggle voice playback",
    ),
    "files": (
        "📁  Files",
        "/getfile <path>             — Send file\n"
        "/listdir [path]             — List directory\n"
        "/download <url>             — Download URL\n"
        "/hide <path>                — Hide file (Win)\n"
        "/show <path>                — Unhide file (Win)\n"
        "/file copy|move|delete <…>  — File ops",
    ),
    "input": (
        "⌨️   Input",
        "/type <text>              — Type text\n"
        "/move <x> <y>             — Move mouse\n"
        "/mousepos                 — Mouse position\n"
        "/mouse click|scroll|drag  — Mouse actions\n"
        "/hotkey <key+key>         — Hotkey combo\n"
        "/msg <text>               — Popup dialog",
    ),
    "processes": (
        "⚙️   Processes",
        "/tasklist         — List processes\n"
        "/killtask <name>  — Kill process\n"
        "/run <program>    — Launch program\n"
        "/cmd <command>    — Shell command\n"
        "/script <code>    — Run Python inline\n"
        "/runscript <path> — Run Python file",
    ),
    "monitoring": (
        "📊  Monitoring",
        "/monitor <cpu|ram|disk|temp>  — Live monitor\n"
        "/stopmonitor                  — Stop",
    ),
    "network": (
        "🌐  Network",
        "/netcheck             — Check internet connection\n"
        "/wifiscan             — Scan Wi-Fi networks\n"
        "/clipboard get       — Read clipboard\n"
        "/clipboard set <…>   — Write clipboard",
    ),
    "ffmpeg": (
        "🎬  FFmpeg",
        "/ffmpeg         — Check FFmpeg status\n"
        "/ffmpeg_install — Download & install FFmpeg",
    ),
    "ip": (
        "🌍  IP & Location",
        "/myip                — Public + local IP addresses\n"
        "/iplookup [ip]       — Geo/ISP lookup (self or given IP)\n"
        "/vpncheck            — Detect VPN/proxy/hosting IP\n"
        "/location            — Send IP-based location pin\n"
        "/gps                 — Real GPS fix (Win), IP fallback\n"
        "/locationlive <sec>  — Live location for N seconds",
    ),
}

_HEADER = "🦉 *OwlBot — Remote Control*"
_FOOTER = "💡 _/help — show this menu at any time_"


def build_help(loaded_modules: list[str]) -> str:
    """
    Return a formatted Markdown help string for *only* the active modules.

    Parameters
    ----------
    loaded_modules:
        Ordered list of module names currently registered in the bot
        (e.g. ``["system", "screen", "audio"]``).
    """
    parts: list[str] = [_HEADER, ""]
    for mod in loaded_modules:
        entry = _MODULE_HELP.get(mod)
        if entry is None:
            continue
        title, cmds = entry
        parts.append(f"*{title}*")
        parts.append(f"```\n{cmds}\n```")
    parts.append("")
    parts.append(_FOOTER)
    return "\n".join(parts)


def build_module_section(module_name: str) -> str:
    """Return the Markdown block for a single module (used by the inline menu)."""
    entry = _MODULE_HELP.get(module_name)
    if entry is None:
        return "❓ Unknown module."
    title, cmds = entry
    return f"*{title}*\n```\n{cmds}\n```"


def module_titles(loaded_modules: list[str]) -> list[tuple[str, str]]:
    """Return ``[(module_name, display_title), ...]`` for loaded modules that have help entries."""
    return [
        (mod, _MODULE_HELP[mod][0])
        for mod in loaded_modules
        if mod in _MODULE_HELP
    ]


__all__ = ["build_help", "build_module_section", "module_titles"]
