# 🦉 OwlBot — Telegram üzerinden modüler Windows uzaktan kontrol ajanı

**OwlBot**, **Telegram** üzerinden çalıştırılan **Windows** için üretime hazır, modüler bir uzaktan kontrol ajanıdır. Sistem kaynaklarını izlemenize, dosyaları yönetmenize, çevre birimlerini kontrol etmenize, ekran/webcam yakalamanıza ve daha fazlasına — hepsi telefonunuzdan — olanak tanır.

---

## ✨ Özellikler

- 🧩 **%100 Modüler** — sadece ihtiyacınız olan modülleri yükleyin
- 💉 **Bağımlılık Enjeksiyonlu Çekirdek** — ek platformlar için hazır (Discord, SSH, …)
- 🛡️ **Kullanıcı ID Beyaz Listesi** ve merkezi hata yönetimi
- 📊 **Canlı kaynak izleme** (CPU, RAM, Disk, sıcaklık)
- 🎹 **Çevre birimi kontrolü** — klavye, fare, kısayollar, ses seviyesi
- 📸 **Ekran yakalama, webcam, zamanlayıcı çekim ve ekran yayını**
- 🔊 **Ses kaydı, ses seviyesi kontrolü ve gelen ses mesajları oynatma**

---

## 🚀 Hızlı Başlangıç

### Ön Koşullar

- Python **3.11+**
- Windows (bazı modüller Win32 API gerektirir)
- `ffmpeg` `PATH` içinde ses oynatma için ([ffmpeg.org](https://ffmpeg.org/) adresinden indirin)
- Bir [Telegram Bot Token](https://t.me/BotFather)

### PyPI'den Kurulum

```bash
# Tam kurulum (Windows + çapraz platform)
pip install owlbot-remote[all]

# Sadece çapraz platform alt kümesi (ses yok, klavye yok, WMI yok)
pip install owlbot-remote
```

### Minimum Dağıtım Scripti

```python
from owlbot import OwlBot

bot = OwlBot(
    token="BOT_TOKENINIZ",
    authorized_users=[123456789],       # Telegram Kullanıcı ID'niz
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

Ya da CLI giriş noktası üzerinden:

```bash
owlbot --token BOT_TOKENINIZ --users 123456789,987654321
```

---

## 📝 Loglama

Varsayılan olarak OwlBot hem konsola **hem de** döngülü bir log dosyasına (`geçerli dizinde owlbot.log`) yazar. Her şey yapılandırılabilir:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="BOT_TOKENINIZ",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None veya "" ile dosya loglamasını devre dışı bırak
    enable_logging=True,     # False ile loglamayı tamamen devre dışı bırak
)
```

| Hedef | Ayar |
|--------|---------|
| Konsol + dosya (varsayılan) | varsayılanı bırakın |
| Sadece konsol, diskte dosya yok | `log_file=None` |
| Tamamen sessiz (ne konsol ne dosya) | `enable_logging=False` |

Aynı seçenekler CLI'den de kullanılabilir:

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # ayrıntılı loglama
owlbot --token TOKEN --users 123 --no-log-file        # sadece konsol, dosya yok
owlbot --token TOKEN --users 123 --disable-logging    # tamamen sessiz
```

---

## 🕹️ Kullanılabilir Modüller ve Komutlar

| Modül | Komut | Açıklama |
|--------|---------|-------------|
| **system** | `/status` | CPU, RAM, Disk, Ağ, Batarya |
| | `/uptime` | Sistem uptime süresi |
| | `/ping` | Sağlık kontrolü |
| | `/lock` | Çalışma alanını kilitle |
| | `/shutdown` | PC'yi kapat |
| | `/restart` | PC'yi yeniden başlat |
| **screen** | `/screenshot` | Masaüstü yakala |
| | `/webcam` | Webcam fotoğrafı çek |
| | `/timelapse <s> <n>` | Periyodik ekran görüntüleri |
| | `/startstream` | Ekran yayını başlat |
| | `/stopstream` | Durdur ve video gönder |
| **input** | `/type <metin>` | Metin yaz |
| | `/move <x> <y>` | Fareyi taşı |
| | `/mousepos` | Fare konumu al |
| | `/mouse <eylem>` | Tıkla / kaydır / sürükle |
| | `/hotkey <k1+k2>` | Kısayol gönder |
| | `/msg <metin>` | Mesaj kutusu göster |
| **audio** | `/mute` / `/unmute` | Sessize al / aç |
| | `/volume <0‑100>` | Ses seviyesi ayarla |
| | `/startrec [sn]` | Mikrofon kaydet |
| | `/stoprec` | Durdur ve gönder |
| | `/playvoice` | Gelen ses mesajlarını oyna |
| **files** | `/listdir [yol]` | Dizin listele |
| | `/getfile <yol>` | Dosya indir |
| | `/hide` / `/show` | Gizli özelliği değiştir |
| | `/file copy/move/delete` | Dosya işlemleri |
| **processes** | `/tasklist` | Çalışan süreçleri listele |
| | `/killtask <exe>` | Süreci sonlandır |
| | `/run` / `/cmd` / `/script` | Komutları çalıştır |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | Periyodik uyarılar |
| | `/stopmonitor` | Uyarıları durdur |
| **network** | `/wifiscan` | Wi-Fi ağlarını tara |
| | `/clipboard get\|set` | Panoya oku/yaz |

---

## 📂 Proje Yapısı

```
owlbot/
├── __init__.py           # Paket exportları ve versiyon
├── config/               # BotConfig dataclass
├── core/
│   ├── bot.py            # Ana OwlBot motoru
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # Paylaşılan yardımcı fonksiyonlar
├── modules/
│   ├── base.py           # BaseModule arayüzü
│   ├── system.py         # Sistem kontrolü
│   ├── screen.py         # Ekran/webcam/yayın
│   ├── files.py          # Dosya işlemleri
│   ├── processes.py      # Süreç yönetimi
│   ├── input.py          # Klavye/fare (Windows)
│   ├── audio.py          # Ses kontrolü (Windows)
│   ├── monitoring.py     # Kaynak izleme
│   └── network.py        # Wi‑Fi / panoya
└── platform/
    └── telegram.py       # Telegram adaptörü
```

---

## 🧪 Testler

Test paketi `pytest` kullanır ve gerçek ağ/Telegram çağrıları yapmaz.

```bash
pip install -e .[dev]
pytest -v
```

Lint (CI ile eşleşir, yapılandırma `.flake8` içinde):

```bash
flake8 src tests
```

---

## 🔧 Kurulum Ekstraları

| Ekstra | İçerir |
|--------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | Yukarıdakilerin tümü |
| `owlbot-remote[dev]` | Geliştirme/CI araçları (`build`, `flake8`, `pytest`) |

---

## 📄 Lisans

**MIT Lisansı** altında dağıtılmaktadır. Detaylar için `LICENSE` dosyasına bakın.

---

* **Sepehr H.I** tarafından sürdürülmektedir 🦉*