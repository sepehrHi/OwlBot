# 🦉 OwlBot — 通过 Telegram 远程控制 Windows 的模块化代理

**OwlBot** 是一个面向生产环境的模块化远程控制代理，专为 **Windows** 设计，通过 **Telegram** 操作。它允许你监控系统资源、管理文件、控制外设、捕获屏幕/摄像头画面等 — 全部通过手机完成。

---

## ✨ 功能特性

- 🧩 **100% 模块化** — 仅加载你需要的模块
- 💉 **依赖注入核心** — 可扩展至其他平台
- 🛡️ **用户 ID 白名单** 和集中式错误处理
- 📊 **实时资源监控** (CPU、内存、磁盘、温度)
- 🎹 **外设控制** — 键盘、鼠标、热键、音量
- 📸 **屏幕截图、摄像头、延时摄影、屏幕流**
- 🔊 **语音录制、音量控制、语音消息播放**

---

## 🚀 快速开始

### 前置要求

- Python **3.11+**
- Windows (部分模块需要 Win32 API)
- `ffmpeg` 在 `PATH` 中 (语音播放需要，从 [ffmpeg.org](https://ffmpeg.org/) 下载)
- 一个 [Telegram Bot Token](https://t.me/BotFather)

### 从 PyPI 安装

```bash
# 完整安装，包含所有功能
pip install owlbot-remote[all]

# 仅跨平台子集 (无音频、无键盘、无 WMI)
pip install owlbot-remote
```

### 最小部署脚本

```python
from owlbot import OwlBot

bot = OwlBot(
    token="你的_BOT_TOKEN",
    authorized_users=[123456789],       # 你的 Telegram 用户 ID
    modules=["system", "screen", "files", "input", "processes", "monitoring"],
)
bot.run()
```

或通过 CLI 入口点：

```bash
owlbot --token 你的_BOT_TOKEN --users 123456789,987654321
```

---

## 📝 日志记录

默认情况下，OwlBot 同时记录到控制台 **和** 一个轮转日志文件 (`owlbot.log`)。所有选项均可配置：

```python
from owlbot import OwlBot

bot = OwlBot(
    token="你的_BOT_TOKEN",
    authorized_users=[123456789],
    log_level="DEBUG",       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    log_file="owlbot.log",   # None 或 "" 禁用文件日志
    enable_logging=True,     # False 完全禁用日志
)
```

| 目标 | 设置 |
|------|--------|
| 控制台 + 文件 (默认) | 保持默认 |
| 仅控制台，无磁盘文件 | `log_file=None` |
| 完全静默 (无控制台、无文件) | `enable_logging=False` |

CLI 同样支持：

```bash
owlbot --token TOKEN --users 123 --log-level DEBUG   # 详细日志
owlbot --token TOKEN --users 123 --no-log-file        # 仅控制台
owlbot --token TOKEN --users 123 --disable-logging    # 完全静默
```

---

## 🕹️ 可用模块与命令

| 模块 | 命令 | 说明 |
|------|------|------|
| **system** | `/status` | CPU、内存、磁盘、网络、电池 |
| | `/uptime` | 系统运行时间 |
| | `/ping` | 健康检查 |
| | `/lock` | 锁定工作站 |
| | `/shutdown` | 关机 |
| | `/restart` | 重启 |
| **screen** | `/screenshot` | 截取桌面 |
| | `/webcam` | 摄像头拍照 |
| | `/timelapse <s> <n>` | 定时截图系列 |
| | `/startstream` | 开始屏幕流 |
| | `/stopstream` | 停止并发送视频 |
| **input** | `/type <文本>` | 模拟输入文本 |
| | `/move <x> <y>` | 移动鼠标 |
| | `/mousepos` | 获取鼠标位置 |
| | `/mouse <动作>` | 点击/滚动/拖拽 |
| | `/hotkey <k1+k2>` | 发送热键 |
| | `/msg <文本>` | 显示消息框 |
| **audio** | `/mute` / `/unmute` | 静音/取消静音 |
| | `/volume <0‑100>` | 设置音量 |
| | `/startrec [秒]` | 录制麦克风 |
| | `/stoprec` | 停止并发送录音 |
| | `/playvoice` | 切换语音播放 |
| **files** | `/listdir [路径]` | 列出目录 |
| | `/getfile <路径>` | 下载文件 |
| | `/hide` / `/show` | 切换隐藏属性 |
| | `/file copy/move/delete` | 文件操作 |
| **processes** | `/tasklist` | 列出进程 |
| | `/killtask <exe>` | 结束进程 |
| | `/run` / `/cmd` / `/script` | 执行命令 |
| **monitoring** | `/monitor <cpu\|ram\|disk\|temp>` | 周期性告警 |
| | `/stopmonitor` | 停止告警 |
| **network** | `/wifiscan` | 扫描 Wi-Fi |
| | `/clipboard get\|set` | 读/写剪贴板 |

---

## 📂 项目结构

```
owlbot/
├── __init__.py           # 包导出与版本
├── config/               # BotConfig 数据类
├── core/
│   ├── bot.py            # OwlBot 主引擎
│   ├── decorators.py     # @authorized_only / @safe_reply
│   └── utils.py          # 共享工具函数
├── modules/
│   ├── base.py           # BaseModule 接口
│   ├── system.py         # 系统控制
│   ├── screen.py         # 屏幕/摄像头/流
│   ├── files.py          # 文件操作
│   ├── processes.py      # 进程管理
│   ├── input.py          # 键盘/鼠标 (Windows)
│   ├── audio.py          # 音频控制 (Windows)
│   ├── monitoring.py     # 资源监控
│   └── network.py        # Wi‑Fi / 剪贴板
└── platform/
    └── telegram.py       # Telegram 适配器
```

---

## 🧪 测试

测试套件使用 `pytest`，不进行真实网络/Telegram 调用。

```bash
pip install -e .[dev]
pytest -v
```

代码检查 (与 CI 一致，配置在 `.flake8`)：

```bash
flake8 src tests
```

---

## 🔧 安装额外依赖

| Extra | 包含内容 |
|-------|---------|
| `owlbot-remote[ui]` | `pyautogui`, `opencv‑python`, `numpy` |
| `owlbot-remote[windows]` | `wmi`, `pycaw`, `keyboard`, `pywifi`, `pyaudio` |
| `owlbot-remote[all]` | 以上全部 |
| `owlbot-remote[dev]` | 开发/CI 工具 (`build`, `flake8`, `pytest`) |

---

## 📄 许可证

基于 **MIT 许可证** 分发。详见 `LICENSE`。

---

*由 **Sepehr H.I** 🦉 维护*