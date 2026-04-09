#!/bin/bash
# 保存当前会话到MemPalace
# 用法: ./mempal_save_hook.sh <会话目录路径>

SESSION_DIR="${1:-$HOME/chats}"
WING="${2:-openclaw_session}"

echo "📦 开始保存会话到 MemPalace..."
echo "   目录: $SESSION_DIR"
echo "   翼楼: $WING"

# 挖掘对话
mempalace mine "$SESSION_DIR" --mode convos --extract general --wing "$WING"

# 更新关键事实
echo "📝 更新关键事实..."
mempalace wake-up --wing "$WING" > ~/.openclaw/critical_facts.txt

echo "✅ 保存完成！"
echo ""
echo "📊 当前状态:"
mempalace status --wing "$WING" 2>/dev/null || mempalace status
