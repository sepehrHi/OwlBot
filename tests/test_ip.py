"""
Tests for owlbot.modules.ip.IPModule's pure helpers (no real network calls).
"""
from __future__ import annotations

from owlbot.modules.ip import IPModule


# ── _looks_like_target ──────────────────────────────────────────────────────

def test_looks_like_target_accepts_ipv4():
    assert IPModule._looks_like_target("8.8.8.8") is True


def test_looks_like_target_accepts_hostname():
    assert IPModule._looks_like_target("example.com") is True


def test_looks_like_target_rejects_spaces():
    assert IPModule._looks_like_target("8.8.8.8 ; rm -rf") is False


def test_looks_like_target_rejects_empty():
    assert IPModule._looks_like_target("") is False


def test_looks_like_target_rejects_shell_metacharacters():
    assert IPModule._looks_like_target("8.8.8.8`whoami`") is False


# ── _format_myip ─────────────────────────────────────────────────────────────

def test_format_myip_with_public_and_local():
    text = IPModule._format_myip("1.2.3.4", ["192.168.1.5", "10.0.0.2"])
    assert "1.2.3.4" in text
    assert "192.168.1.5" in text
    assert "10.0.0.2" in text


def test_format_myip_without_public_ip_shows_warning():
    text = IPModule._format_myip(None, [])
    assert "could not determine" in text
    assert "none found" in text


# ── _format_iplookup ─────────────────────────────────────────────────────────

def test_format_iplookup_success():
    data = {
        "status": "success", "query": "8.8.8.8", "city": "Mountain View",
        "regionName": "California", "country": "United States",
        "countryCode": "US", "zip": "94043", "timezone": "America/Los_Angeles",
        "lat": 37.4, "lon": -122.1, "isp": "Google LLC", "org": "Google LLC",
        "proxy": False, "hosting": True, "mobile": False,
    }
    text = IPModule._format_iplookup(data, "8.8.8.8")
    assert "Mountain View" in text
    assert "Google LLC" in text
    assert "hosting/datacenter IP" in text
    assert "✅ No" in text  # proxy flag


def test_format_iplookup_failure():
    data = {"status": "fail", "message": "invalid query"}
    text = IPModule._format_iplookup(data, "not-an-ip")
    assert "failed" in text.lower()
    assert "invalid query" in text


# ── _format_vpncheck ─────────────────────────────────────────────────────────

def test_format_vpncheck_detects_proxy():
    data = {"status": "success", "query": "1.1.1.1", "isp": "X", "org": "Y", "proxy": True, "hosting": False}
    text = IPModule._format_vpncheck(data)
    assert "Likely using a VPN" in text


def test_format_vpncheck_clean_ip():
    data = {"status": "success", "query": "1.1.1.1", "isp": "X", "org": "Y", "proxy": False, "hosting": False}
    text = IPModule._format_vpncheck(data)
    assert "No VPN/proxy detected" in text


def test_format_vpncheck_failure():
    data = {"status": "fail", "message": "boom"}
    text = IPModule._format_vpncheck(data)
    assert "failed" in text.lower()


# ── _windows_gps ─────────────────────────────────────────────────────────────

def test_windows_gps_returns_false_on_non_windows(monkeypatch):
    monkeypatch.setattr("owlbot.modules.ip.sys.platform", "linux")
    ok, reason = IPModule._windows_gps()
    assert ok is False
    assert "Windows" in reason


# ── _get_local_ips ───────────────────────────────────────────────────────────

def test_get_local_ips_returns_list():
    ips = IPModule._get_local_ips()
    assert isinstance(ips, list)
    assert all(isinstance(ip, str) for ip in ips)
    assert all(not ip.startswith("127.") for ip in ips)


# ── IPModule instance state (/gpslive, /stopgpslive) ─────────────────────────

def test_init_gps_live_state_is_idle():
    mod = IPModule(config=None, bot=None, auth=lambda f: f, safe=lambda f: f)
    assert mod._gps_live_active is False
    assert mod._gps_live_thread is None
