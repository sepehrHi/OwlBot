# 🦉 OwlBot — Agente de control remoto modular para Windows vía Telegram

**OwlBot** es un agente de control remoto modular listo para producción para **Windows**, operado a través de **Telegram**. Te permite monitorizar recursos del sistema, gestionar archivos, controlar periféricos, capturar pantalla/webcam y más — todo desde tu móvil.

---

## ✨ Características

- 🧩 **100% Modular** — carga solo los módulos que necesitas
- 💉 **Núcleo con inyección de dependencias** — listo para plataformas extra (Discord, SSH, …)
- 🛡️ **Lista blanca de User-ID** y manejo de errores centralizado
- 📊 **Monitorización en vivo de recursos** (CPU, RAM, Disco, temperatura)
- 🎹 **Control de periféricos** — teclado, ratón, atajos, volumen de audio
- 📸 **Captura de pantalla, webcam, timelapse y streaming de pantalla**
- 🔊 **Grabación de voz, control de volumen y reproducción de mensajes de voz entrantes**

---

## 🚀 Inicio rápido

### Requisitos previos

- Python **3.11+**
- Windows (algunos módulos requieren Win32 API)
- `ffmpeg` en `PATH` si usas reproducción de voz (descarga desde [ffmpeg.org](https://ffmpeg.org/))
- Un [Token de Bot de Telegram](https://t.me/BotFather)

### Instalación desde PyPI

```bash
# Instalación completa con todas las funciones (Windows + multiplataforma)
pip install owlbot-remote[all]

# Solo subconjunto multiplataforma (sin audio, sin teclado, sin WMI)
pip install owlbot-remote
```

### Script mínimo de despliegue

```python
from owlbot import OwlBot

bot = OwlBot(
    token="TU_BOT_TOKEN",
    authorized_users=[123456789],       # tu ID de usuario de Telegram
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

O vía el punto de entrada CLI:

```bash
owlbot --token TU_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 Logging

Por defecto OwlBot registra tanto en consola **como** en un archivo de log rotativo (`owlbot.log` en el directorio actual). Todo es configurable:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="TU_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None o "" para desactivar archivo de log
    enable_logging=True,     # False para desactivar logging completamente
)
```

| Objetivo | Configuración |
|--------|-------------|
| Consola + archivo (por defecto) | dejar por defecto |
| Solo consola, sin archivo en disco | `log_file=None` |
| Completamente silencioso (ni consola ni archivo) | `enable_logging=False` |

Mismas opciones desde CLI:

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # logging verboso
owlbot --token TOKEN --users 123 --no-log-file        # solo consola, sin archivo
owlbot --token TOKEN --users 123 --disable-logging    # completamente silencioso
```

---

## 🕹️ Módulos y comandos disponibles

| Módulo | Comando | Descripción |
|--------|---------|-------------|
| **system** | `/status` | CPU, RAM, Disco, Red, Batería |
| | `/uptime` | Tiempo de actividad del sistema |
| | `/ping` | Health-check |
| | `/lock` | Bloquear estación de trabajo |
| | `/shutdown` | Apagar PC |
| | `/restart` | Reiniciar PC |
| **screen** | `/screenshot` | Capturar escritorio |
| | `/webcam` | Capturar foto de webcam |
| | `/timelapse <s> <n>` | Serie de capturas |
| | `/startstream` | Iniciar streaming de pantalla |
| | `/stopstream` | Detener y enviar video |
| **input** | `/type <texto>` | Escribir texto |
| | `/move <x> <y>` | Mover ratón |
| | `/mousepos` | Obtener posición del ratón |
| | `/mouse <acción>` | Click / scroll / drag |
| | `/hotkey <k1+k2>` | Enviar atajo |
| | `/msg <texto>` | Mostrar cuadro de mensaje |
| **audio** | `/mute` / `/unmute` | Alternar mute |
| | `/volume <0‑100>` | Establecer volumen |
| | `/startrec [seg]` | Grabar micrófono |
| | `/stoprec` | Detener y enviar grabación |
| | `/playvoice` | Alternar reproducción de voz entrante |
| **files** | `/listdir [ruta]` | Listar directorio |
| | `/getfile <ruta>` | Descargar archivo |
| | `/hide` / `/show` | Alternar atributo hidden |
| | `/file copy/move/delete` | Operaciones de archivo |
| **processes** | `/tasklist` | Listar procesos en ejecución |
| | `/killtask <exe>` | Matar proceso |
| | `/run` / `/cmd` / `/script` | Ejecutar comandos |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Alertas periódicas |
| | `/stopmonitor` | Detener alertas |
| **network** | `/wifiscan` | Escanear redes Wi‑Fi |
| | `/clipboard get\|set` | Leer/escribir portapapeles |

---

## 📂 Estructura del proyecto

```
owlbot/
├── __init__.py           # Exportaciones del paquete y versión
├── config/               # Dataclass BotConfig
├── core/
│   ├── bot.py            # Motor principal OwlBot
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Utilidades compartidas
├── modules/
│   ├── base.py           # Interfaz BaseModule
│   ├── system.py         # Control de sistema
│   ├── screen.py         # Pantalla/webcam/stream
│   ├── files.py          # Operaciones de archivo
│   ├── processes.py      # Gestión de procesos
│   ├── input.py          # Teclado/ratón (Windows)
│   ├── audio.py          # Control de audio (Windows)
│   ├── monitoring.py     # Monitorización de recursos
│   └── network.py        # Wi‑Fi / portapapeles
└── platform/
    └── telegram.py       # Adaptador Telegram
```

---

## 🧪 Tests

La suite de tests usa `pytest` y no hace llamadas reales de red/Telegram.

```bash
pip install -e .[dev]
pytest -v
```

Lint (coincide con CI, config en `.flake8`):

```bash
flake8 src tests
```

---

## 🔧 Extras de instalación

| Extra | Incluye |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Todo lo anterior |
| `owlbot-remote[dev]` | Herramientas Dev/CI (`build`, `flake8`, `pytest`) |

---

## 📄 Licencia

Distribuido bajo la **Licencia MIT**. Ver `LICENSE` para detalles.

---

*Mantenido por **Sepehr H.I** 🦉*