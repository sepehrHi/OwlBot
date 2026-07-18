# 🦉 OwlBot — Modulaire Telegram remote control agent voor Windows

**OwlBot** is een productie-klaar, modulair remote-control agent voor **Windows**, bediend via **Telegram**. Hiermee bewaak je systeembronnen, beheer je bestanden, controleer je randapparaten, maak je scherm/webcam-opnames en meer — allemaal vanuit je telefoon.

---

## ✨ Functies

- 🧩 **100% Modulair** — laad alleen de modules die je nodig hebt
- 💉 **Dependency-injection kernel** — klaar voor extra platforms (Discord, SSH, …)
- 🛡️ **Gebruikers-ID whitelist** en gecentraliseerde foutafhandeling
- 📊 **Live resource monitoring** (CPU, RAM, Schijf, temperatuur)
- 🎹 **Randapparaatbesturing** — toetsenbord, muis, sneltoetsen, audio-volume
- 📸 **Schermopname, webcam, timelapse en scherm-streaming**
- 🔊 **Spraakopname, volumeregeling en afspelen van inkomende spraakberichten**

---

## 🚀 Snelstart

### Vereisten

- Python **3.11+**
- Windows (sommige modules vereisen Win32 API)
- `ffmpeg` in `PATH` voor spraakafspelen (download van [ffmpeg.org](https://ffmpeg.org/))
- Een [Telegram Bot Token](https://t.me/BotFather)

### Installatie via PyPI

```bash
# Volledige installatie met alle functies (Windows + cross-platform)
pip install owlbot-remote[all]

# Alleen cross-platform subset (geen audio, geen toetsenbord, geen WMI)
pip install owlbot-remote
```

### Minimaal deploy-script

```python
from owlbot import OwlBot

bot = OwlBot(
    token="JOUW_BOT_TOKEN",
    authorized_users=[123456789],       # jouw Telegram gebruikers-ID
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

Of via de CLI entry-point:

```bash
owlbot --token JOUW_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 Logging

Standaard logt OwlBot zowel naar de console **als** naar een draaiend logbestand (`owlbot.log` in de huidige map). Alles is configureerbaar:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="JOUW_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None of "" om bestand-logging uit te schakelen
    enable_logging=True,     # False om logging volledig uit te schakelen
)
```

| Doel | Instelling |
|------|----------|
| Console + bestand (standaard) | standaard laten |
| Alleen console, geen bestand op schijf | `log_file=None` |
| Volledig stil (geen console, geen bestand) | `enable_logging=False` |

Deze opties zijn ook via CLI beschikbaar:

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # gedetailleerd loggen
owlbot --token TOKEN --users 123 --no-log-file        # alleen console, geen bestand
owlbot --token TOKEN --users 123 --disable-logging    # volledig stil
```

---

## 🕹️ Beschikbare modules & commando's

| Module | Commando | Beschrijving |
|--------|---------|-------------|
| **system** | `/status` | CPU, RAM, Schijf, Netwerk, Batterij |
| | `/uptime` | Systeem uptime |
| | `/ping` | Health-check |
| | `/lock` | Werkstation vergrendelen |
| | `/shutdown` | PC uitschakelen |
| | `/restart` | PC herstarten |
| **screen** | `/screenshot` | Bureaublad vastleggen |
| | `/webcam` | Webcam foto maken |
| | `/timelapse <s> <n>` | Reeks screenshots |
| | `/startstream` | Scherm-streaming starten |
| | `/stopstream` | Stoppen & video sturen |
| **input** | `/type <tekst>` | Tekst typen |
| | `/move <x> <y>` | Muis verplaatsen |
| | `/mousepos` | Muispositie opvragen |
| | `/mouse <actie>` | Klik / scroll / sleep |
| | `/hotkey <k1+k2>` | Sneltoets sturen |
| | `/msg <tekst>` | Berichtvenster tonen |
| **audio** | `/mute` / `/unmute` | Dempen aan/uit |
| | `/volume <0‑100>` | Volume instellen |
| | `/startrec [sec]` | Microfoon opnemen |
| | `/stoprec` | Stoppen & opname sturen |
| | `/playvoice` | Inkomende spraakberichten afspelen |
| **files** | `/listdir [pad]` | Map weergeven |
| | `/getfile <pad>` | Bestand downloaden |
| | `/hide` / `/show` | Verborgen attribuut togglen |
| | `/file copy/move/delete` | Bestandsbewerkingen |
| **processes** | `/tasklist` | Draaiende processen lijsten |
| | `/killtask <exe>` | Proces beëindigen |
| | `/run` / `/cmd` / `/script` | Commando's uitvoeren |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Periodieke alerts |
| | `/stopmonitor` | Alerts stoppen |
| **network** | `/wifiscan` | Wi-Fi netwerken scannen |
| | `/clipboard get\|set` | Klembord lezen/schrijven |

---

## 📂 Projectstructuur

```
owlbot/
├── __init__.py           # Package exports & versie
├── config/               # BotConfig dataclass
├── core/
│   ├── bot.py            # Hoofd OwlBot engine
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Gedeelde hulpfuncties
├── modules/
│   ├── base.py           # BaseModule interface
│   ├── system.py         # Systeembesturing
│   ├── screen.py         # Scherm/webcam/stream
│   ├── files.py          # Bestandsbewerkingen
│   ├── processes.py      # Procesbeheer
│   ├── input.py          # Toetsenbord/muis (Windows)
│   ├── audio.py          # Audio-besturing (Windows)
│   ├── monitoring.py     # Resource monitoring
│   └── network.py        # Wi‑Fi / klembord
└── platform/
    └── telegram.py       # Telegram adapter
```

---

## 🧪 Tests

De testsuite gebruikt `pytest` en doet geen echte netwerk/Telegram-aanroepen.

```bash
pip install -e .[dev]
pytest -v
```

Lint (overeenkomend met CI, config in `.flake8`):

```bash
flake8 src tests
```

---

## 🔧 Installatie-extras

| Extra | Bevat |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Alles bovenstaande |
| `owlbot-remote[dev]` | Dev/CI tools (`build`, `flake8`, `pytest`) |

---

## 📄 Licentie

Uitgegeven onder de **MIT-licentie**. Zie `LICENSE` voor details.

---

*Onderhouden door **Sepehr H.I** 🦉*