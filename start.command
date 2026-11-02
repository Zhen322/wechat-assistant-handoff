#!/bin/zsh
set -eu
TASK_DIR="${0:A:h}"
exec "$TASK_DIR/文案助手/wechat-writer/start.command"
