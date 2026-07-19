"""
IP module — /myip, /iplookup, /vpncheck, /location, /gps, /locationlive
Cross-platform IP + geolocation lookups, plus a best-effort real GPS fix
on Windows (via Windows Location Services) with automatic IP-based fallback.

Privacy note: every command here reveals the *device's* network identity
and/or approximate physical location. Access is already gated by the
existing @auth (authorized_users) decorator, same trust boundary as
/shutdown, /run, /screenshot, etc. — this module does not add a new
attack surface, it only exposes more about the machine you already
control.
"""
from __future__ import annotations

import logging
import re
import socket
import subprocess
import sys

import requests

from owlbot.core.utils import animate_message, finish_animation
from owlbot.modules.base import BaseModule

logger = logging.getLogger("owlbot.modules.ip")

# ip-api.com free tier is HTTP-only (HTTPS requires a paid plan) and allows
# picking exactly the fields we need via `fields=`.
_GEO_FIELDS = (
    "status,message,country,countryCode,regionName,city,zip,lat,lon,"
    "timezone,isp,org,as,proxy,hosting,mobile,query"
)
_GEO_URL = "http://ip-api.com/json/{target}"
_PUBLIC_IP_URL = "https://api.ipify.org?format=json"

_TARGET_RE = re.compile(r"^[A-Za-z0-9.:_-]{1,253}$")

# Queries Windows Location Services (System.Device.Location) for a real
# GPS / Wi-Fi-triangulated fix. Requires Location to be enabled in
# Windows Settings → Privacy → Location for the calling process.
_GPS_PS_SCRIPT = r"""
Add-Type -AssemblyName System.Device
$watcher = New-Object System.Device.Location.GeoCoordinateWatcher
$watcher.Start()
$elapsed = 0
while ($watcher.Status -ne 'Ready' -and $watcher.Permission -ne 'Denied' -and $elapsed -lt 10) {
    Start-Sleep -Milliseconds 500
    $elapsed += 0.5
}
if ($watcher.Permission -eq 'Denied') {
    Write-Output "DENIED"
} elseif ($watcher.Position.Location.IsUnknown) {
    Write-Output "UNKNOWN"
} else {
    $c = $watcher.Position.Location
    Write-Output "$($c.Latitude),$($c.Longitude),$($c.HorizontalAccuracy)"
}
$watcher.Stop()
"""


class IPModule(BaseModule):
    name = "ip"

    # ── Pure helpers (unit-testable, no bot/network side effects) ──────────

    @staticmethod
    def _looks_like_target(value: str) -> bool:
        """Loose validation for an optional IP/hostname argument."""
        return bool(value) and " " not in value and bool(_TARGET_RE.match(value))

    @staticmethod
    def _get_local_ips() -> list[str]:
        """Best-effort collection of this machine's local (LAN) IPv4 addresses."""
        ips: set[str] = set()
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
                ip = info[4][0]
                if not ip.startswith("127."):
                    ips.add(ip)
        except OSError:
            logger.debug("getaddrinfo failed while collecting local IPs", exc_info=True)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1.0)
                s.connect(("8.8.8.8", 80))
                ips.add(s.getsockname()[0])
        except OSError:
            logger.debug("UDP-connect trick failed while collecting local IPs", exc_info=True)
        return sorted(ips)

    @staticmethod
    def _fetch_public_ip(timeout: float = 5.0) -> str | None:
        """Return this machine's public IP address, or None on failure."""
        try:
            resp = requests.get(_PUBLIC_IP_URL, timeout=timeout)
            resp.raise_for_status()
            return resp.json().get("ip")
        except (requests.RequestException, ValueError):
            logger.debug("public IP lookup failed", exc_info=True)
            return None

    @staticmethod
    def _fetch_geo(target: str | None = None, timeout: float = 6.0) -> dict:
        """
        Geolocate an IP/hostname via ip-api.com, or the caller's own public
        IP when *target* is None. Always returns a dict with at least a
        "status" key ("success" | "fail") — never raises.
        """
        url = _GEO_URL.format(target=target.strip() if target else "")
        try:
            resp = requests.get(url, params={"fields": _GEO_FIELDS}, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.debug("geo lookup failed: %s", exc)
            return {"status": "fail", "message": "Network error or lookup service unavailable."}

    @staticmethod
    def _format_myip(public_ip: str | None, local_ips: list[str]) -> str:
        pub = public_ip or "⚠️ could not determine (no internet?)"
        local_block = "\n".join(f"  • {ip}" for ip in local_ips) if local_ips else "  • none found"
        return (
            "```\n"
            "🌐  Your IP Addresses\n"
            f"{'─' * 32}\n"
            f"Public : {pub}\n"
            f"Local  :\n{local_block}\n"
            "```"
        )

    @staticmethod
    def _format_iplookup(data: dict, requested: str | None) -> str:
        if data.get("status") != "success":
            reason = data.get("message", "unknown error")
            return f"❌ *IP lookup failed:* {reason}"
        proxy_flag = "⚠️ Yes" if data.get("proxy") else "✅ No"
        extra = []
        if data.get("hosting"):
            extra.append("🏢 hosting/datacenter IP")
        if data.get("mobile"):
            extra.append("📱 mobile network")
        extra_txt = f" ({', '.join(extra)})" if extra else ""
        lines = [
            "```",
            f"🌍  IP Lookup — {data.get('query', requested or '?')}",
            "─" * 34,
            f"📍  {data.get('city', '?')}, {data.get('regionName', '?')}, {data.get('country', '?')}",
            f"🏳️  {data.get('countryCode', '?')}   ZIP: {data.get('zip', '?')}",
            f"🕒  Timezone: {data.get('timezone', '?')}",
            f"🛰️  Coords: {data.get('lat', '?')}, {data.get('lon', '?')}",
            f"🏢  ISP: {data.get('isp', '?')}",
            f"🏗️  Org: {data.get('org', '?')}",
            f"🔌  Proxy/VPN: {proxy_flag}{extra_txt}",
            "```",
        ]
        return "\n".join(lines)

    @staticmethod
    def _format_vpncheck(data: dict) -> str:
        if data.get("status") != "success":
            return f"❌ *VPN check failed:* {data.get('message', 'unknown error')}"
        is_proxy = bool(data.get("proxy"))
        is_hosting = bool(data.get("hosting"))
        verdict = (
            "⚠️ *Likely using a VPN / proxy / datacenter IP*"
            if (is_proxy or is_hosting)
            else "✅ *No VPN/proxy detected*"
        )
        return (
            f"{verdict}\n\n"
            f"IP: `{data.get('query', '?')}`\n"
            f"ISP: {data.get('isp', '?')}\n"
            f"Org: {data.get('org', '?')}\n"
            f"Proxy flag: {'Yes' if is_proxy else 'No'}\n"
            f"Hosting/Datacenter flag: {'Yes' if is_hosting else 'No'}\n\n"
            "_Detection is heuristic (ip-api.com) and not 100% reliable._"
        )

    @staticmethod
    def _windows_gps(timeout: float = 15.0) -> tuple[bool, str]:
        """
        Attempt a real GPS / Wi-Fi-triangulated fix via Windows Location
        Services. Returns (True, "lat,lon,accuracy") on success, or
        (False, reason) on failure/non-Windows.
        """
        if sys.platform != "win32":
            return False, "Real GPS is only available on Windows."
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", _GPS_PS_SCRIPT],
                capture_output=True, text=True, timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return False, f"Could not query Windows Location Services: {exc}"

        output = (result.stdout or "").strip()
        if output == "DENIED":
            return False, "Location access denied — enable it in Windows Settings → Privacy → Location."
        if output == "UNKNOWN" or not output:
            return False, "No GPS/location fix available (service disabled or no signal)."
        return True, output

    # ── Handlers ─────────────────────────────────────────────────────────

    def register(self) -> None:  # noqa: C901
        bot, auth, safe = self.bot, self.auth, self.safe

        @bot.message_handler(commands=["myip"])
        @auth
        @safe
        def cmd_myip(message: object) -> None:
            bot.send_chat_action(message.chat.id, "typing")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["🌐 *Checking IP addresses…* ⏳", "🌐 *Checking IP addresses…* ⏳⏳"],
            )
            public_ip = self._fetch_public_ip()
            local_ips = self._get_local_ips()
            finish_animation(bot, anim_msg, message.chat.id, self._format_myip(public_ip, local_ips))

        @bot.message_handler(commands=["iplookup"])
        @auth
        @safe
        def cmd_iplookup(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            target = parts[1].strip() if len(parts) > 1 else None
            if target and not self._looks_like_target(target):
                bot.reply_to(message, "❌ That doesn't look like a valid IP or hostname.")
                return

            bot.send_chat_action(message.chat.id, "typing")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["🌍 *Looking up IP…* ⏳", "🌍 *Looking up IP…* ⏳⏳", "🌍 *Looking up IP…* ⏳⏳⏳"],
            )
            data = self._fetch_geo(target)
            finish_animation(bot, anim_msg, message.chat.id, self._format_iplookup(data, target))

        @bot.message_handler(commands=["vpncheck"])
        @auth
        @safe
        def cmd_vpncheck(message: object) -> None:
            bot.send_chat_action(message.chat.id, "typing")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["🕵️ *Checking for VPN/proxy…* ⏳", "🕵️ *Checking for VPN/proxy…* ⏳⏳"],
            )
            data = self._fetch_geo(None)
            finish_animation(bot, anim_msg, message.chat.id, self._format_vpncheck(data))

        @bot.message_handler(commands=["location"])
        @auth
        @safe
        def cmd_location(message: object) -> None:
            bot.send_chat_action(message.chat.id, "find_location")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["📍 *Finding location (IP-based)…* ⏳", "📍 *Finding location (IP-based)…* ⏳⏳"],
            )
            data = self._fetch_geo(None)
            if data.get("status") != "success":
                finish_animation(bot, anim_msg, message.chat.id, f"❌ {data.get('message', 'lookup failed')}")
                return
            finish_animation(
                bot, anim_msg, message.chat.id,
                f"📍 Approximate location (IP-based) — {data.get('city', '?')}, {data.get('country', '?')}",
            )
            bot.send_location(message.chat.id, data["lat"], data["lon"])

        @bot.message_handler(commands=["gps"])
        @auth
        @safe
        def cmd_gps(message: object) -> None:
            bot.send_chat_action(message.chat.id, "find_location")
            anim_msg = animate_message(
                bot, message.chat.id,
                ["🛰️ *Requesting real GPS fix…* ⏳", "🛰️ *Requesting real GPS fix…* ⏳⏳", "🛰️ *Requesting real GPS fix…* ⏳⏳⏳"],
            )
            ok, payload = self._windows_gps()
            if ok:
                lat_s, lon_s, acc_s = payload.split(",")
                lat, lon = float(lat_s), float(lon_s)
                try:
                    acc = float(acc_s)
                    acc_txt = f"±{acc:.0f}m"
                except ValueError:
                    acc_txt = "unknown accuracy"
                finish_animation(bot, anim_msg, message.chat.id, f"🛰️ *Real GPS fix* ({acc_txt})")
                bot.send_location(message.chat.id, lat, lon)
                return

            # Fall back to IP-based location
            data = self._fetch_geo(None)
            if data.get("status") != "success":
                finish_animation(
                    bot, anim_msg, message.chat.id,
                    f"❌ Real GPS unavailable ({payload}) and IP fallback also failed.",
                )
                return
            finish_animation(
                bot, anim_msg, message.chat.id,
                f"⚠️ Real GPS unavailable ({payload})\nFalling back to IP-based location (approximate).",
            )
            bot.send_location(message.chat.id, data["lat"], data["lon"])

        @bot.message_handler(commands=["locationlive"])
        @auth
        @safe
        def cmd_locationlive(message: object) -> None:
            parts = message.text.split(maxsplit=1)  # type: ignore[attr-defined]
            if len(parts) < 2 or not parts[1].strip().isdigit():
                bot.reply_to(
                    message,
                    "📍 Usage: `/locationlive <seconds>` (60–86400)",
                    parse_mode="Markdown",
                )
                return
            seconds = max(60, min(int(parts[1].strip()), 86400))

            bot.send_chat_action(message.chat.id, "find_location")
            data = self._fetch_geo(None)
            if data.get("status") != "success":
                bot.reply_to(message, f"❌ {data.get('message', 'lookup failed')}")
                return

            bot.send_location(message.chat.id, data["lat"], data["lon"], live_period=seconds)
            bot.reply_to(
                message,
                f"📍 *Live location started* for {seconds}s (IP-based — a stationary PC won't move on the map).",
                parse_mode="Markdown",
            )
