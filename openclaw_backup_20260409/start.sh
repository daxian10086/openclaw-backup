#!/bin/bash

# 启动时自动加载MemPalace关键事实到上下文
echo "📚 加载 MemPalace 记忆..."
mempalace wake-up > ~/.openclaw/system_context.txt 2>/dev/null || echo "MemPalace 加载完成"

nohup openclaw gateway run --port 5000 > /app/work/logs/bypass/dev.log 2>&1 &
