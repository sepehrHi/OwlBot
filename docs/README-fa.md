# 🦉 OwlBot — عامل کنترل از راه دور ماژولار برای ویندوز از طریق تلگرام

**OwlBot** یک عامل کنترل از راه دور ماژولار و آماده‌تولید برای **ویندوز** است که از طریق **تلگرام** vận hành می‌شود. این ربات به شما امکان می‌دهد منابع سیستم را نظارت کنید، فایل‌ها را مدیریت کنید، محیط‌های جانبی را کنترل کنید، از صفحه نمایش/وب‌کم عکس بگیرید، و کارهای دیگر را — همه از گوشی‌تان انجام دهید.

---

## ✨ امکانات

- 🧩 **۱۰۰٪ ماژولار** — تنها ماژول‌های مورد نیاز را بارگذاری کنید
- 💉 **هسته وابستگی‌ریز (DI)** — برای پلتفرم‌های اضافی (Discord، SSH، …) آماده
- 🛡️ **لیست سفید شناسه کاربری** و مدیریت خطای متمرکز
- 📊 **نظارت منابع زنده** (CPU، RAM، دیسک، دما)
- 🎹 **کنترل محیط‌های جانبی** — کیبورد، موس، میان‌برها، حجم صدا
- 📸 **برداشت از صفحه، وب‌کم، تایم‌لپس، و استریم صفحه**
- 🔊 **ضبط صدا، کنترل حجم، و پخش پیام‌های صوتی دریافتی**

---

## 🚀 شروع سریع

### پیش‌نیازها

- Python **3.11+**
- ویندوز (برخی ماژول‌ها به Win32 API نیاز دارند)
- `ffmpeg` در `PATH` اگر از پخش صدا استفاده می‌کنید (دانلود از [ffmpeg.org](https://ffmpeg.org/))
- یک [توکن ربات تلگرام](https://t.me/BotFather)

### نصب از PyPI

```bash
# نصب کامل با تمام امکانات (ویندوز + چندپلتفرمی)
pip install owlbot-remote[all]

# فقط زیرمجموعه چندپلتفرمی (بدون صدا، بدون کیبورد، بدون WMI)
pip install owlbot-remote
```

### اسکریپت مینیمال استقرار

```python
from owlbot import OwlBot

bot = OwlBot(
    token="توکن_ربات_شما",
    authorized_users=[123456789],       # شناسه کاربری تلگرام شما
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

یا از طریق نقطه ورود CLI:

```bash
owlbot --token توکن_ربات_شما --users 123456789,987654321
```

---

## 📝 لاگ‌گیری

به طور پیش‌فرض OwlBot هم در کنسول **و** هم در یک فایل لاگ چرخشی (`owlbot.log` در دایرکتوری جاری) لاگ می‌نویسد. همه چیز قابل تنظیم است:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="توکن_ربات_شما",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None یا "" برای غیرفعال کردن فایل لاگ
    enable_logging=True,     # False برای غیرفعال کردن کامل لاگ‌گیری
)
```

| هدف | تنظیم |
|------|--------|
| کنسول + فایل (پیش‌فرض) | پیش‌فرض را نگه دارید |
| فقط کنسول، فایل روی دیسک نیست | `log_file=None` |
| کاملاً بی‌صدا (نه کنسول، نه فایل) | `enable_logging=False` |

همان گزینه‌ها از CLI هم در دسترس هستند:

```bash
owlbot --token توکن --users 123 --log-level DEBUG   # لاگ‌گیری پرمخاطب
owlbot --token توکن --users 123 --no-log-file        # فقط کنسول، فایل نیست
owlbot --token توکن --users 123 --disable-logging    # کاملاً بی‌صدا
```

---

## 🕹️ ماژول‌ها و دستورات موجود

| ماژول | دستور | توضیح |
|--------|---------|-------------|
| **system** | `/status` | CPU، RAM، دیسک، شبکه، باتری |
| | `/uptime` | آپ‌تایم سیستم |
| | `/ping` | هلت-چک |
| | `/lock` | قفل 워کستیشن |
| | `/shutdown` | خاموش کردن PC |
| | `/restart` | ریستارت PC |
| **screen** | `/screenshot` | برداشت از دسکتاپ |
| | `/webcam` | عکس وب‌کم |
| | `/timelapse <s> <n>` | سری عکس‌برداری |
| | `/startstream` | استریم صفحه |
| | `/stopstream` | توقف و ارسال ویدیو |
| **input** | `/type <متن>` | تایپ متن |
| | `/move <x> <y>` | حرکت موس |
| | `/mousepos` | موقعیت موس |
| | `/mouse <عمل>` | کلیک / اسکرول / ドラッグ |
| | `/hotkey <k1+k2>` | ارسال میان‌بر |
| | `/msg <متن>` | نمایش باکس پیام |
| **audio** | `/mute` / `/unmute` | توگل میوت |
| | `/volume <0‑100>` | تنظیم حجم |
| | `/startrec [ثانیه]` | ضبط میکروفون |
| | `/stoprec` | توقف و ارسال ضبط |
| | `/playvoice` | توگل پخش پیام‌های صوتی |
| **files** | `/listdir [مسیر]` | لیست دایرکتوری |
| | `/getfile <مسیر>` | دانلود فایل |
| | `/hide` / `/show` | توگل مخفی |
| | `/file copy/move/delete` | عملیات فایل |
| **processes** | `/tasklist` | لیست پروسه‌ها |
| | `/killtask <exe>` | کشتن پروسه |
| | `/run` / `/cmd` / `/script` | اجرای دستورات |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | هشدارهای دوره‌ای |
| | `/stopmonitor` | توقف هشدارها |
| **network** | `/wifiscan` | اسکن وای‌فای |
| | `/clipboard get\|set` | خواندن/نوشتن کلیپ‌بورد |

---

## 📂 ساختار پروژه

```
owlbot/
├── __init__.py           # صادرات بسته و نسخه
├── config/               # دیتاکلاس BotConfig
├── core/
│   ├── bot.py            # موتور اصلی OwlBot
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # توابع مشترک
├── modules/
│   ├── base.py           # اینترفیس BaseModule
│   ├── system.py         # کنترل سیستم
│   ├── screen.py         # صفحه/وب‌کم/استریم
│   ├── files.py          # عملیات فایل
│   ├── processes.py      # مدیریت پروسه
│   ├── input.py          # کیبورد/موس (ویندوز)
│   ├── audio.py          # کنترل صدا (ویندوز)
│   ├── monitoring.py     # نظارت منابع
│   └── network.py        # وای‌فای / کلیپ‌بورد
└── platform/
    └── telegram.py       # آداپتور تلگرام
```

---

## 🧪 تست

مجموعه تست از `pytest` استفاده می‌کند و تماس واقعی شبکه/تلگرام انجام نمی‌دهد.

```bash
pip install -e .[dev]
pytest -v
```

لینت (مطابق CI، کانفیگ در `.flake8`):

```bash
flake8 src tests
```

---

## 🔧 اکسترای نصب

| Extra | شامل |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | همه موارد بالا |
| `owlbot-remote[dev]` | ابزارهای Dev/CI (`build`, `flake8`, `pytest`) |

---

## 📄 لایسنس

توزیع شده تحت **لایسنس MIT**. برای جزئیات `LICENSE` را ببینید.

---

*توسعه‌دهنده: **Sepehr H.I** 🦉*