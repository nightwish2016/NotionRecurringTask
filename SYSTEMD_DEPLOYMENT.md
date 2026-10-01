# 定时任务部署说明

本文记录本次将 `cron + start.sh` 调整为 Python 虚拟环境与
systemd timer 的相关命令和知识点。

## 原方案的问题

原定时任务：

```cron
02 16 * * * bash /root/mytools/NotionRecurringTask/start.sh > /root/mytools/NotionRecurringTask/result.log 2>&1
```

检查后发现：

- `start.sh` 引用的 `notionVenv` 目录已经不存在。
- 系统 Python 缺少 `python-dotenv`。
- `.env` 的加载依赖当前工作目录，在定时任务环境中不够可靠。
- 服务器使用 UTC 时区。UTC 的 `16:02` 是北京时间次日 `00:02`，
  不是北京时间 `16:02`。
- 当前执行环境不能使用 `crontab` 命令安装用户级 cron 任务。

## Python 虚拟环境

创建虚拟环境：

```bash
cd /root/mytools/NotionRecurringTask
python3 -m venv .venv
```

如果 Ubuntu/Debian 提示 `ensurepip is not available`，先安装对应组件：

```bash
sudo apt update
sudo apt install python3-venv
```

安装项目及依赖：

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

也可以按照 `requirements.txt` 安装：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

`-e .` 表示以 editable 模式安装当前项目。修改 `Src` 中的代码后，
通常不需要重新安装项目。

虚拟环境不一定要通过 `source .venv/bin/activate` 使用。定时任务中直接
调用解释器路径更可靠：

```bash
/root/mytools/NotionRecurringTask/.venv/bin/python \
  /root/mytools/NotionRecurringTask/Src/main.py
```

## 启动脚本

当前 `start.sh` 使用：

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/Src/main.py"
```

相关知识点：

- `set -e`：命令失败时终止脚本。
- `set -u`：使用未定义变量时报错。
- `set -o pipefail`：管道中任意命令失败时，整个管道返回失败。
- `${BASH_SOURCE[0]}`：取得当前脚本路径，避免依赖调用者的工作目录。
- `exec`：用 Python 进程替换 shell 进程，使退出码和信号直接传递给
  systemd。

检查脚本语法：

```bash
bash -n start.sh systemd/install.sh
```

赋予执行权限：

```bash
chmod 755 start.sh systemd/install.sh
```

## 环境变量

程序显式加载项目根目录下的 `.env`：

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")
```

这避免了从其他目录启动程序时找不到 `.env`。

`.env` 包含 Notion 凭据和数据库 ID，不应提交到 Git。限制文件权限：

```bash
chmod 600 /root/mytools/NotionRecurringTask/.env
```

权限 `600` 表示只有文件所有者能够读写。

## systemd service

`systemd/notion-recurring-task.service` 定义一次任务执行：

```ini
[Service]
Type=oneshot
WorkingDirectory=/root/mytools/NotionRecurringTask
ExecStart=/root/mytools/NotionRecurringTask/start.sh
Environment=PYTHONUNBUFFERED=1
UMask=0077
StandardOutput=append:/root/mytools/NotionRecurringTask/result.log
StandardError=append:/root/mytools/NotionRecurringTask/result.log
```

相关知识点：

- `Type=oneshot`：运行一次命令，命令结束后服务结束。
- `WorkingDirectory`：设置程序工作目录。
- `PYTHONUNBUFFERED=1`：Python 日志立即输出，避免缓冲导致日志延迟。
- `UMask=0077`：任务创建的文件默认只允许当前用户访问。
- `StandardOutput` 和 `StandardError`：将标准输出和错误追加到
  `result.log`。
- `After/Wants=network-online.target`：任务依赖网络，尽量等待网络就绪。

## systemd timer

`systemd/notion-recurring-task.timer` 使用：

```ini
[Timer]
OnCalendar=*-*-* 00:02:00 Asia/Shanghai
Persistent=true
RandomizedDelaySec=0
Unit=notion-recurring-task.service
```

相关知识点：

- `OnCalendar`：定义日历时间。
- `Asia/Shanghai`：显式指定北京时间，不受服务器 UTC 时区影响。
- `Persistent=true`：如果关机期间错过执行，开机后会补跑一次。
- `RandomizedDelaySec=0`：不增加随机延迟。

本配置表示每天北京时间 `00:02` 执行。

## 安装并启用定时器

项目提供了一键安装脚本：

```bash
sudo /root/mytools/NotionRecurringTask/systemd/install.sh
```

脚本执行的核心命令为：

```bash
sudo install -m 0644 systemd/notion-recurring-task.service \
  /etc/systemd/system/notion-recurring-task.service
sudo install -m 0644 systemd/notion-recurring-task.timer \
  /etc/systemd/system/notion-recurring-task.timer
sudo systemctl daemon-reload
sudo systemctl enable --now notion-recurring-task.timer
```

- `daemon-reload`：让 systemd 重新读取 unit 文件。
- `enable`：设置开机自动启用。
- `--now`：在启用的同时立即启动 timer。
- 启动 timer 不会立即执行 service，而是等待下一个计划时间。

## 状态检查与手动运行

查看下一次执行时间：

```bash
systemctl list-timers notion-recurring-task.timer --no-pager
```

查看 timer 状态：

```bash
systemctl status notion-recurring-task.timer --no-pager
```

手动执行一次任务：

```bash
sudo systemctl start notion-recurring-task.service
```

查看 service 状态：

```bash
systemctl status notion-recurring-task.service --no-pager
```

查看 systemd 日志：

```bash
journalctl -u notion-recurring-task.service -n 100 --no-pager
```

查看项目日志：

```bash
tail -n 100 /root/mytools/NotionRecurringTask/result.log
```

直接运行启动脚本：

```bash
cd /root/mytools/NotionRecurringTask
./start.sh
```

直接运行会访问并修改 Notion 数据，只应在确认配置正确时执行。

## 修改定时配置

修改 `systemd/notion-recurring-task.timer` 后，重新安装并加载：

```bash
sudo /root/mytools/NotionRecurringTask/systemd/install.sh
```

例如改为每天北京时间 `08:30`：

```ini
OnCalendar=*-*-* 08:30:00 Asia/Shanghai
```

## 停用与重新启用

停用：

```bash
sudo systemctl disable --now notion-recurring-task.timer
```

重新启用：

```bash
sudo systemctl enable --now notion-recurring-task.timer
```

## 常用验证命令

检查 Python 文件语法：

```bash
.venv/bin/python -m py_compile \
  Src/main.py \
  Src/NotionRecurringTask/*.py \
  Src/NotionRecurringTask/Notion/*.py
```

检查关键依赖：

```bash
.venv/bin/python -c "import dotenv, requests; print('dependencies ok')"
```

检查 Git 改动是否包含空白错误：

```bash
git diff --check
```
