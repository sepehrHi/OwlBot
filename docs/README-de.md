# 🦉 OwlBot — Modulare Fernsteuerung für Windows über Telegram

**OwlBot** ist ein produktionsreifer, modulärer Fernsteuerungs-Agent für **Windows**, der über **Telegram** bedient wird. Er ermöglicht die Überwachung von Systemressourcen, Dateiverwaltung, Peripherie-Steuerung, Bildschirm/Webcam-Aufnahmen und mehr — alles vom Smartphone aus.

---

## ✨ Funktionen

- 🧩 **100 % Modular** — lade nur die Module, die du brauchst
- 💉 **Dependency-Injection-Kern** — bereit für zusätzliche Plattformen (Discord, SSH, …)
- 🛡️ **User-ID-Whitelist** und zentrales Fehlerhandling
- 📊 **Live-Ressourcenüberwachung** (CPU, RAM, Festplatte, Temperatur)
- 🎹 **Peripherie-Steuerung** — Tastatur, Maus, Hotkeys, Audio-Lautstärke
- 📸 **Bildschirmaufnahme, Webcam, Timelapse und Bildschirm-Streaming**
- 🔊 **Sprachaufnahme, Lautstärkeregelung und Wiedergabe eingehender Sprachnachrichten**

---

## 🚀 Schnellstart

### Voraussetzungen

- Python **3.11+**
- Windows (einige Module benötigen Win32 API)
- `ffmpeg` im `PATH` für Sprachwiedergabe (Download von [ffmpeg.org](https://ffmpeg.org/))
- Ein [Telegram Bot Token](https://t.me/BotFather)

### Installation via PyPI

```bash
# Vollinstallation mit allen Features (Windows + Cross-Platform)
pip install owlbot-remote[all]

# Nur Cross-Platform-Subset (kein Audio, keine Tastatur, kein WMI)
pip install owlbot-remote
```

### Minimales Deployment-Skript

```python
from owlbot import OwlBot

bot = OwlBot(
    token="DEIN_BOT_TOKEN",
    authorized_users=[123456789],       # deine Telegram User ID
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

Oder über den CLI-Entry-Point:

```bash
owlbot --token DEIN_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 Logging

Standardmäßig loggt OwlBot sowohl auf der Konsole **als auch** in eine rotierende Log-Datei (`owlbot.log` im aktuellen Verzeichnis). Alles ist konfigurierbar:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="DEIN_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None oder "" um Log-Datei zu deaktivieren
    enable_logging=True,     # False um Logging komplett zu deaktivieren
)
```

| Ziel | Einstellung |
|------|-----------|
| Konsole + Datei (Standard) | Standard belassen |
| Nur Konsole, keine Datei auf Platte | `log_file=None` |
| Vollständig stumm (keine Konsole, keine Datei) | `enable_logging=False` |

Gleiche Optionen via CLI:

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # ausführliches Logging
owlbot --token TOKEN --users 123 --no-log-file        # nur Konsole, keine Datei
owlbot --token TOKEN --users 123 --disable-logging    # komplett stumm
```

---

## 🕹️ Verfügbare Module & Befehle

| Modul | Befehl | Beschreibung |
|-------|--------|--------------|
| **system** | `/status` | CPU, RAM, Festplatte, Netzwerk, Akku |
| | `/uptime` | System-Uptime |
| | `/ping` | Health-Check |
| | `/lock` | Arbeitsstation sperren |
| | `/shutdown` | PC herunterfahren |
| | `/restart` | PC neu starten |
| **screen** | `/screenshot` | Desktop aufnehmen |
| | `/webcam` | Webcam-Foto aufnehmen |
| | `/timelapse <s> <n>` | Screenshot-Serie |
| | `/startstream` | Bildschirm-Streaming starten |
| | `/stopstream` | Stoppen & Video senden |
| **input** | `/type <text>` | Text eingeben |
| | `/move <x> <y>` | Maus bewegen |
| | `/mousepos` | Mausposition abrufen |
| | `/mouse <aktion>` | Klick / Scroll / Drag |
| | `/hotkey <k1+k2>` | Hotkey senden |
| | `/msg <text>` | Messagebox anzeigen |
| **audio** | `/mute` / `/unmute` | Stummschaltung umschalten |
| | `/volume <0‑100>` | Lautstärke setzen |
| | `/startrec [sek]` | Mikrofon aufnehmen |
| | `/stoprec` | Aufnehmen stoppen & senden |
| | `/playvoice` | Eingehende Sprachnachrichten wiedergeben |
| **files** | `/listdir [pfad]` | Verzeichnis auflisten |
| | `/getfile <pfad>` | Datei herunterladen |
| | `/hide` / `/show` | Hidden-Attribut umschalten |
| | `/file copy/move/delete` | Dateioperationen |
| **processes** | `/tasklist` | Laufende Prozesse auflisten |
| | `/killtask <exe>` | Prozess beenden |
| | `/run` / `/cmd` / `/script` | Befehle ausführen |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Periodische Alerts |
| | `/stopmonitor` | Alerts stoppen |
| **network** | `/wifiscan` | Wi-Fi-Netze scannen |
| | `/clipboard get\|set` | Zwischenablage lesen/schreiben |

---

## 📂 Projektstruktur

```
owlbot/
├── __init__.py           # Paket-Exports & Version
├── config/               # BotConfig Dataclass
├── core/
│   ├── bot.py            # Haupt-OwlBot-Engine
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Geteilte Helfer
├── modules/
│   ├── base.py           # BaseModule Interface
│   ├── system.py         # Systemsteuerung
│   ├── screen.py         # Bildschirm/Webcam/Stream
│   ├── files.py          # Dateioperationen
│   ├── processes.py      # Prozessverwaltung
│   ├── input.py          # Tastatur/Maus (Windows)
│   ├── audio.py          # Audio-Steuerung (Windows)
│   ├── monitoring.py     # Ressourcenüberwachung
│   └── network.py        # Wi‑Fi / Zwischenablage
└── platform/
    └── telegram.py       # Telegram-Adapter
```

---

## 🧪 Tests

Die Test-Suite nutzt `pytest` und macht keine echten Netzwerk-/Telegram-Aufrufe.

```bash
pip install -e .[dev]
pytest -v
```

Lint (entspricht CI, Config in `.flake8`):

```bash
flake8 src tests
```

---

## 🔧 Installations-Extras

| Extra | Enthält |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Alles oben |
| `owlbot-remote[dev]` | Dev/CI-Tools (`build`, `flake8`, `pytest`) |

---

## 📄 Lizenz

Vertrieben unter der **MIT-Lizenz**. Siehe `LICENSE` für Details.

---

*Gepflegt von **Sepehr H.I** 🦉*