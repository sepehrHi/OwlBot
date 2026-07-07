"""
Tests for owlbot.modules.monitoring.MonitoringModule's pure metric readers.
"""
from __future__ import annotations

from owlbot.modules.monitoring import MonitoringModule


def test_read_cpu_returns_percentage_string():
    result = MonitoringModule._read_cpu()
    assert result.startswith("📊 CPU:")
    assert result.endswith("%")


def test_read_ram_returns_percentage_and_gb():
    result = MonitoringModule._read_ram()
    assert result.startswith("📊 RAM:")
    assert "GB" in result


def test_read_disk_returns_percentage_and_gb():
    result = MonitoringModule._read_disk()
    assert result.startswith("📊 Disk:")
    assert "GB" in result


def test_read_temp_without_wmi_client_reports_windows_only():
    result = MonitoringModule._read_temp(None)
    assert "Windows" in result


def test_read_temp_with_no_probes_reports_unavailable():
    class _FakeWmi:
        def Win32_TemperatureProbe(self):
            return []

    result = MonitoringModule._read_temp(_FakeWmi())
    assert "not available" in result


def test_read_temp_with_probe_reports_celsius():
    class _FakeProbe:
        CurrentReading = 350  # tenths of a degree -> 35.0°C

    class _FakeWmi:
        def Win32_TemperatureProbe(self):
            return [_FakeProbe()]

    result = MonitoringModule._read_temp(_FakeWmi())
    assert "35.0" in result


def test_init_wmi_client_returns_none_on_non_windows(monkeypatch):
    monkeypatch.setattr("owlbot.modules.monitoring.sys.platform", "linux")
    assert MonitoringModule._init_wmi_client() is None
