#!/usr/bin/env bash
set -euo pipefail

SYSTEMD_DIR=/etc/systemd/system
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

install -m 0644 \
    "$SCRIPT_DIR/notion-recurring-task.service" \
    "$SYSTEMD_DIR/notion-recurring-task.service"
install -m 0644 \
    "$SCRIPT_DIR/notion-recurring-task.timer" \
    "$SYSTEMD_DIR/notion-recurring-task.timer"

systemctl daemon-reload
systemctl enable --now notion-recurring-task.timer
systemctl list-timers notion-recurring-task.timer --no-pager
