#!/bin/bash
# 启动 MemPalace 会话监听服务（后台运行）

SESSIONS_DIR="${1:-/workspace/projects/agents/main/sessions}"
WING="${2:-openclaw_session}"
PID_FILE="/tmp/mempalace_watch.pid"
LOG_FILE="/tmp/mempalace_watch.log"

echo "🚀 启动 MemPalace 会话监听服务..."

# 检查是否已经运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $OLD_PID)"
        echo "   使用 'stop_mempalace_watch.sh' 停止服务"
        exit 1
    else
        echo "🧹 清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

# 启动服务（后台运行）
nohup bash /workspace/projects/scripts/mempalace_watch.sh "$SESSIONS_DIR" "$WING" > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# 保存 PID
echo "$NEW_PID" > "$PID_FILE"

echo "✅ 服务已启动"
echo "   PID: $NEW_PID"
echo "   会话目录: $SESSIONS_DIR"
echo "   目标翼楼: $WING"
echo "   日志文件: $LOG_FILE"
echo ""
echo "查看日志: tail -f $LOG_FILE"
echo "停止服务: ./scripts/stop_mempalace_watch.sh"
