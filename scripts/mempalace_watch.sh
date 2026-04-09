#!/bin/bash
# 实时监听 OpenClaw 会话存档，自动导入 MemPalace

SESSIONS_DIR="${1:-/workspace/projects/agents/main/sessions}"
WING="${2:-openclaw_session}"
TEMP_DIR="/tmp/mempalace_import"

echo "📡 MemPalace 会话监听服务启动..."
echo "   会话目录: $SESSIONS_DIR"
echo "   目标翼楼: $WING"
echo "   按 Ctrl+C 停止监听"
echo ""

# 创建临时目录
mkdir -p "$TEMP_DIR"

# 处理会话文件的函数
process_session() {
    local jsonl_file="$1"
    local temp_md="$TEMP_DIR/$(basename "$jsonl_file" .jsonl).md"
    local file_size=$(stat -c%s "$jsonl_file" 2>/dev/null || echo "0")

    # 只处理有内容的文件（> 100 字节）
    if [ "$file_size" -le 100 ]; then
        return
    fi

    # 检查是否已经处理过（基于文件大小）
    local cache_file="$TEMP_DIR/.cache_$(basename "$jsonl_file")"
    if [ -f "$cache_file" ]; then
        local cached_size=$(cat "$cache_file")
        if [ "$cached_size" == "$file_size" ]; then
            return
        fi
    fi

    echo "📦 处理会话: $(basename "$jsonl_file") (${file_size} bytes)"

    # 转换 JSONL 为 Markdown 格式
    python3 << 'PYTHON_EOF' "$jsonl_file" "$temp_md"
import json
import sys
from datetime import datetime

jsonl_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(f"# OpenClaw 会话存档\n")
            out.write(f"**文件**: {jsonl_file}\n")
            out.write(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            out.write("---\n\n")

            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                data_type = data.get('type', '')

                if data_type == 'message':
                    msg = data.get('message', {})
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', [])
                    timestamp = data.get('timestamp', '')

                    # 提取文本内容
                    text_content = ""
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and 'text' in item:
                                text_content += item.get('text', '')
                            elif isinstance(item, dict) and 'type' in item:
                                # 处理其他类型的内容
                                text_content += str(item)

                    if not text_content:
                        continue

                    # 格式化输出
                    role_emoji = {'user': '👤', 'assistant': '🤖', 'system': '⚙️'}.get(role, '❓')

                    out.write(f"{role_emoji} **{role.upper()}**\n")
                    if timestamp:
                        out.write(f"*{timestamp[:19]}*\n")
                    out.write(f"{text_content}\n")
                    out.write("\n---\n\n")

except Exception as e:
    sys.stderr.write(f"Error: {e}\n")
    sys.exit(1)
PYTHON_EOF

    if [ -f "$temp_md" ] && [ -s "$temp_md" ]; then
        # 导入到 MemPalace
        mempalace mine "$TEMP_DIR" --mode convos --wing "$WING" 2>&1 | grep -E "(Processed|Skipped|Filed)" | head -3 || true

        # 记录已处理的文件大小
        echo "$file_size" > "$cache_file"

        echo "✅ 导入完成"
    else
        echo "❌ 转换失败"
    fi

    # 清理临时文件
    rm -f "$temp_md"
}

# 监听会话目录的变化
fswatch -o "$SESSIONS_DIR" | while read -r; do
    # 检查所有最近修改的会话文件
    find "$SESSIONS_DIR" -name "*.jsonl" -mmin -1 -type f | while read -r file; do
        process_session "$file"
    done
done
