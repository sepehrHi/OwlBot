# 🦉 OwlBot — Agent de contrôle à distance modulaire pour Windows via Telegram

**OwlBot** est un agent de contrôle à distance modulaire prêt pour la production pour **Windows**, opéré via **Telegram**. Il vous permet de surveiller les ressources système, gérer les fichiers, contrôler les périphériques, capturer l'écran/webcam et plus — tout depuis votre téléphone.

---

## ✨ Fonctionnalités

- 🧩 **100 % Modulaire** — chargez uniquement les modules dont vous avez besoin
- 💉 **Cœur à injection de dépendances** — prêt pour plateformes supplémentaires (Discord, SSH, …)
- 🛡️ **Liste blanche d'ID utilisateur** et gestion d'erreurs centralisée
- 📊 **Surveillance des ressources en temps réel** (CPU, RAM, Disque, température)
- 🎹 **Contrôle des périphériques** — clavier, souris, raccourcis, volume audio
- 📸 **Capture d'écran, webcam, timelapse et streaming d'écran**
- 🔊 **Enregistrement vocal, contrôle du volume et lecture des messages vocaux entrants**

---

## 🚀 Démarrage rapide

### Prérequis

- Python **3.11+**
- Windows (certains modules nécessitent l'API Win32)
- `ffmpeg` dans `PATH` pour la lecture vocale (téléchargement depuis [ffmpeg.org](https://ffmpeg.org/))
- Un [Token de Bot Telegram](https://t.me/BotFather)

### Installation depuis PyPI

```bash
# Installation complète avec toutes les fonctionnalités (Windows + multi-plateforme)
pip install owlbot-remote[all]

# Sous-ensemble multi-plateforme uniquement (pas d'audio, pas de clavier, pas de WMI)
pip install owlbot-remote
```

### Script de déploiement minimal

```python
from owlbot import OwlBot

bot = OwlBot(
    token="VOTRE_BOT_TOKEN",
    authorized_users=[123456789],       # votre ID utilisateur Telegram
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

Ou via le point d'entrée CLI :

```bash
owlbot --token VOTRE_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 Journalisation

Par défaut, OwlBot journalise à la fois sur la console **et** dans un fichier de log rotatif (`owlbot.log` dans le répertoire courant). Tout est configurable :

```python
from owlbot import OwlBot

bot = OwlBot(
    token="VOTRE_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None ou "" pour désactiver le fichier de log
    enable_logging=True,     # False pour désactiver complètement la journalisation
)
```

| Objectif | Réglage |
|--------|---------|
| Console + fichier (défaut) | laisser par défaut |
| Console seulement, pas de fichier sur disque | `log_file=None` |
| Complètement silencieux (ni console, ni fichier) | `enable_logging=False` |

Mêmes options via CLI :

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # journalisation verbeuse
owlbot --token TOKEN --users 123 --no-log-file        # console seulement, pas de fichier
owlbot --token TOKEN --users 123 --disable-logging    # complètement silencieux
```

---

## 🕹️ Modules et commandes disponibles

| Module | Commande | Description |
|--------|---------|-------------|
| **system** | `/status` | CPU, RAM, Disque, Réseau, Batterie |
| | `/uptime` | Temps de fonctionnement du système |
| | `/ping` | Vérification de santé |
| | `/lock` | Verrouiller la session |
| | `/shutdown` | Éteindre le PC |
| | `/restart` | Redémarrer le PC |
| **screen** | `/screenshot` | Capturer le bureau |
| | `/webcam` | Photo webcam |
| | `/timelapse <s> <n>` | Série de captures |
| | `/startstream` | Démarrer le streaming |
| | `/stopstream` | Arrêter et envoyer la vidéo |
| **input** | `/type <texte>` | Saisir du texte |
| | `/move <x> <y>` | Déplacer la souris |
| | `/mousepos` | Position de la souris |
| | `/mouse <action>` | Clic / défilement / glisser |
| | `/hotkey <k1+k2>` | Envoyer un raccourci |
| | `/msg <texte>` | Afficher une boîte de dialogue |
| **audio** | `/mute` / `/unmute` | Couper/réactiver le son |
| | `/volume <0‑100>` | Régler le volume |
| | `/startrec [sec]` | Enregistrer le micro |
| | `/stoprec` | Arrêter et envoyer l'enregistrement |
| | `/playvoice` | Basculer lecture messages vocaux |
| **files** | `/listdir [chemin]` | Lister un répertoire |
| | `/getfile <chemin>` | Télécharger un fichier |
| | `/hide` / `/show` | Basculer attribut caché |
| | `/file copy/move/delete` | Opérations sur fichiers |
| **processes** | `/tasklist` | Lister les processus |
| | `/killtask <exe>` | Tuer un processus |
| | `/run` / `/cmd` / `/script` | Exécuter des commandes |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Alertes périodiques |
| | `/stopmonitor` | Arrêter les alertes |
| **network** | `/wifiscan` | Scanner les réseaux Wi‑Fi |
| | `/clipboard get\|set` | Lire/écrire le presse-papiers |

---

## 📂 Structure du projet

```
owlbot/
├── __init__.py           # Exports du paquet et version
├── config/               # Dataclass BotConfig
├── core/
│   ├── bot.py            # Moteur principal OwlBot
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Utilitaires partagés
├── modules/
│   ├── base.py           # Interface BaseModule
│   ├── system.py         # Contrôle système
│   ├── screen.py         # Écran/webcam/stream
│   ├── files.py          # Opérations fichiers
│   ├── processes.py      # Gestion processus
│   ├── input.py          # Clavier/souris (Windows)
│   ├── audio.py          # Contrôle audio (Windows)
│   ├── monitoring.py     # Surveillance ressources
│   └── network.py        # Wi‑Fi / presse-papiers
└── platform/
    └── telegram.py       # Adaptateur Telegram
```

---

## 🧪 Tests

La suite de tests utilise `pytest` sans appels réseau/Telegram réels.

```bash
pip install -e .[dev]
pytest -v
```

Lint (correspond à CI, config dans `.flake8`) :

```bash
flake8 src tests
```

---

## 🔧 Extras d'installation

| Extra | Inclut |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Tout ci-dessus |
| `owlbot-remote[dev]` | Outils Dev/CI (`build`, `flake8`, `pytest`) |

---

## 📄 Licence

Distribué sous **Licence MIT**. Voir `LICENSE` pour détails.

---

*Maintenu par **Sepehr H.I** 🦉*