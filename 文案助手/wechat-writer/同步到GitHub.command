#!/bin/zsh
# 一键把本机改动同步到 GitHub（Zhen322/wechat-assistant-handoff）
# 用法：在 Finder 里双击本文件；或在终端执行 ./同步到GitHub.command
set -u

TASK_DIR="${0:A:h}"
cd "$TASK_DIR" || exit 1
export PATH="$HOME/.local/bin:$PATH"
TASK_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "请先克隆交接仓库，再使用同步脚本。"; exit 1; }
cd "$TASK_ROOT" || exit 1
TASK_REMOTE="$(git remote get-url origin 2>/dev/null)"
case "$TASK_REMOTE" in
  https://github.com/Zhen322/wechat-assistant-handoff|https://github.com/Zhen322/wechat-assistant-handoff.git|git@github.com:Zhen322/wechat-assistant-handoff.git) ;;
  *) echo "当前 origin 不是交接仓库，已停止。请核对 git remote -v。"; exit 1 ;;
esac

echo "=================================="
echo "  字里 · 同步到 GitHub"
echo "=================================="
echo

# ---- 0) 安全闸门：绝不提交密钥文件 ----
if git status --porcelain | grep -qE 'wechat-writer/data/(coze_secrets|settings)\.json'; then
  echo "✗ 检测到密钥文件出现在待提交列表中，已中止。"
  echo "  请检查 .gitignore 是否被改动，不要强制提交。"
  echo
  read -k 1 "?按任意键关闭..."
  exit 1
fi

# ---- 1) 有没有新改动 ----
if [[ -z "$(git status --porcelain)" ]]; then
  echo "✓ 本机没有任何新改动，无需同步。"
  echo
  git fetch -q origin 2>/dev/null
  git status -sb | head -1
  echo
  read -k 1 "?按任意键关闭..."
  exit 0
fi

echo "本次将提交以下改动："
echo
git status --short | sed 's/^/  /'
echo

# ---- 2) 提交 ----
STAMP="$(date '+%Y-%m-%d %H:%M')"
git add -A
if ! git commit -q -m "更新：$STAMP"; then
  echo "✗ 提交失败，请把上面的提示发给助手。"
  echo
  read -k 1 "?按任意键关闭..."
  exit 1
fi
echo "✓ 已提交（$STAMP）"
echo

# ---- 3) 推送 ----
echo "正在推送到 GitHub ..."
OUT="$(git push origin main 2>&1)"
RC=$?
echo "$OUT" | tail -4 | sed 's/^/  /'
echo

if [[ $RC -eq 0 ]]; then
  echo "✓ 同步完成：https://github.com/Zhen322/wechat-assistant-handoff"
else
  echo "✗ 推送失败，常见原因："
  echo "  1. GitHub 登录或仓库写入权限未配置，请使用自己的接班账号登录。"
  echo "  2. 网络波动 —— 稍后重试即可。提交已经保存在本机，不会丢。"
fi
echo
read -k 1 "?按任意键关闭..."
