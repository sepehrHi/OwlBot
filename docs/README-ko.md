# 🦉 OwlBot — Telegram을 통한 모듈식 Windows 원격 제어 에이전트

**OwlBot**은 **Telegram**을 통해 작동하는 **Windows**용 프로덕션 준비된 모듈식 원격 제어 에이전트입니다. 시스템 리소스 모니터링, 파일 관리, 주변기기 제어, 화면/웹캠 캡처 등을 휴대폰에서 모두 수행할 수 있습니다.

---

## ✨ 기능

- 🧩 **100% 모듈식** — 필요한 모듈만 로드
- 💉 **의존성 주입 코어** — 추가 플랫폼 지원 가능 (Discord, SSH, …)
- 🛡️ **사용자 ID 화이트리스트** 및 중앙 집중식 오류 처리
- 📊 **실시간 리소스 모니터링** (CPU, RAM, 디스크, 온도)
- 🎹 **주변기기 제어** — 키보드, 마우스, 단축키, 오디오 볼륨
- 📸 **화면 캡처, 웹캠, 타임랩스, 화면 스트리밍**
- 🔊 **음성 녹음, 볼륨 제어, 수신 음성 메시지 재생**

---

## 🚀 빠른 시작

### 사전 요구사항

- Python **3.11+**
- Windows (일부 모듈은 Win32 API 필요)
- `ffmpeg`가 `PATH`에 있어야 음성 재생 가능 ([ffmpeg.org](https://ffmpeg.org/)에서 다운로드)
- [Telegram Bot Token](https://t.me/BotFather)

### PyPI에서 설치

```bash
# 전체 설치 (Windows + 크로스 플랫폼)
pip install owlbot-remote[all]

# 크로스 플랫폼만 (오디오, 키보드, WMI 없음)
pip install owlbot-remote
```

### 최소 배포 스크립트

```python
from owlbot import OwlBot

bot = OwlBot(
    token="내_봇_토큰",
    authorized_users=[123456789],       # 텔레그램 사용자 ID
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

또는 CLI 진입점을 통해:

```bash
owlbot --token 내_봇_토큰 --users 123456789,987654321
```

---

## 📝 로깅

기본적으로 OwlBot은 콘솔 **및** 순환 로그 파일(`owlbot.log`, 현재 디렉터리)에 기록합니다. 모든 설정 가능:

```python
from owlbot import OwlBot

bot = OwlBot(
    token="내_봇_토큰",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None 또는 ""로 파일 로그 비활성화
    enable_logging=True,     # False로 로깅 완전 비활성화
)
```

| 목표 | 설정 |
|------|------------|
| 콘솔 + 파일 (기본) | 기본값 유지 |
| 콘솔만, 디스크에 파일 없음 | `log_file=None` |
| 완전 무음 (콘솔 없음, 파일 없음) | `enable_logging=False` |

CLI에서도 동일 옵션 사용 가능:

```bash
owlbot --token 토큰 --users 123 --log-level DEBUG   # 상세 로깅
owlbot --token 토큰 --users 123 --no-log-file        # 콘솔만, 파일 없음
owlbot --token 토큰 --users 123 --disable-logging    # 완전 무음
```

---

## 🕹️ 사용 가능한 모듈 및 명령어

| 모듈 | 명령어 | 설명 |
|--------|---------|-------------|
| **system** | `/status` | CPU, RAM, 디스크, 네트워크, 배터리 |
| | `/uptime` | 시스템 업타임 |
| | `/ping` | 헬스 체크 |
| | `/lock` | 워크스테이션 잠금 |
| | `/shutdown` | PC 종료 |
| | `/restart` | PC 재시작 |
| **screen** | `/screenshot` | 데스크톱 캡처 |
| | `/webcam` | 웹캠 사진 촬영 |
| | `/timelapse <s> <n>` | 스크린샷 시리즈 |
| | `/startstream` | 화면 스트리밍 시작 |
| | `/stopstream` | 중지 및 비디오 전송 |
| **input** | `/type <텍스트>` | 텍스트 입력 |
| | `/move <x> <y>` | 마우스 이동 |
| | `/mousepos` | 마우스 위치 가져오기 |
| | `/mouse <동작>` | 클릭 / 스크롤 / 드래그 |
| | `/hotkey <k1+k2>` | 단축키 전송 |
| | `/msg <텍스트>` | 메시지 박스 표시 |
| **audio** | `/mute` / `/unmute` | 음소거 토글 |
| | `/volume <0‑100>` | 볼륨 설정 |
| | `/startrec [초]` | 마이크 녹음 |
| | `/stoprec` | 중지 및 녹음 전송 |
| | `/playvoice` | 수신 음성 메시지 재생 토글 |
| **files** | `/listdir [경로]` | 디렉터리 나열 |
| | `/getfile <경로>` | 파일 다운로드 |
| | `/hide` / `/show` | 숨김 속성 토글 |
| | `/file copy/move/delete` | 파일 작업 |
| **processes** | `/tasklist` | 실행 중인 프로세스 나열 |
| | `/killtask <exe>` | 프로세스 종료 |
| | `/run` / `/cmd` / `/script` | 명령 실행 |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | 주기적 알림 |
| | `/stopmonitor` | 알림 중지 |
| **network** | `/wifiscan` | Wi-Fi 네트워크 스캔 |
| | `/clipboard get\|set` | 클립보드 읽기/쓰기 |

---

## 📂 프로젝트 구조

```
owlbot/
├── __init__.py           # 패키지 내보내기 및 버전
├── config/               # BotConfig 데이터클래스
├── core/
│   ├── bot.py            # 메인 OwlBot 엔진
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # 공유 유틸리티
├── modules/
│   ├── base.py           # BaseModule 인터페이스
│   ├── system.py         # 시스템 제어
│   ├── screen.py         # 화면/웹캠/스트림
│   ├── files.py          # 파일 작업
│   ├── processes.py      # 프로세스 관리
│   ├── input.py          # 키보드/마우스 (Windows)
│   ├── audio.py          # 오디오 제어 (Windows)
│   ├── monitoring.py     # 리소스 모니터링
│   └── network.py        # Wi‑Fi / 클립보드
└── platform/
    └── telegram.py       # 텔레그램 어댑터
```

---

## 🧪 테스트

테스트 스위트는 `pytest`를 사용하며 실제 네트워크/텔레그램 호출을 하지 않습니다.

```bash
pip install -e .[dev]
pytest -v
```

린트 (CI와 일치, 설정은 `.flake8`에):

```bash
flake8 src tests
```

---

## 🔧 설치 추가 기능

| 추가 기능 | 포함 사항 |
|--------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | 위 모든 것 |
| `owlbot-remote[dev]` | 개발/CI 도구 (`build`, `flake8`, `pytest`) |

---

## 📄 라이선스

**MIT 라이선스** 하에 배포. 자세한 내용은 `LICENSE` 참조.

---

* **Sepehr H.I** 님이 유지 관리 🦉*