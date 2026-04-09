#!/bin/bash
# 停止 MemPalace 会话监听服务

PID_FILE="/tmp/mempalace_watch.pid"

echo "🛑 停止 MemPalace 会话监听服务..."

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  PID 文件不存在"
else
    OLD_PID=$(cat "$PID_FILE")

    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        # 杀死主进程及其子进程
        pkill -P "$OLD_PID"
        kill "$OLD_PID"
        echo "✅ 服务已停止 (PID: $OLD_PID)"
    else
        echo "⚠️  进程已不存在"
    fi

    rm -f "$PID_FILE"
fi

# 确保所有相关进程都被清理
pkill -f "mempalace_watch.sh" 2>/dev/null || true
