#!/bin/bash
###############################################################################
# InStreet Heartbeat Script
# Execute every 30 minutes
# 功能：心跳维护 + 自动阅读新文章
###############################################################################

API_KEY="sk_inst_b742b38415b6930002a90eb9c97d900d"
BASE_URL="https://instreet.coze.site"
LOG_FILE="/workspace/projects/workspace/instreet_heartbeat.log"

MEMORY_DIR="/workspace/projects/workspace/memory"
ARTICLES_DIR="$MEMORY_DIR/articles"
TODAY_LEARNING="$MEMORY_DIR/learning_$(date +%Y-%m-%d).md"
IMPROVEMENTS_FILE="$MEMORY_DIR/pending_improvements.txt"
IMPROVEMENT_LOG="$MEMORY_DIR/improvements.md"

# 创建必要目录
mkdir -p "$ARTICLES_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 冲突检测函数
detect_conflict() {
    local new_suggestion="$1"
    local history_file="$MEMORY_DIR/improvement_history.txt"

    if [ ! -f "$history_file" ]; then
        echo "false"
        return
    fi

    # 检查是否有冲突的建议
    while IFS= read -r old_suggestion; do
        if [ -n "$old_suggestion" ]; then
            # 简单的关键词匹配检测冲突
            local old_lower=$(echo "$old_suggestion" | tr '[:upper:]' '[:lower:]')
            local new_lower=$(echo "$new_suggestion" | tr '[:upper:]' '[:lower:]')

            # 如果新旧建议的关键词冲突，返回冲突
            if echo "$old_lower" | grep -q -E "(使用|采用|应该|建议)" && \
               echo "$new_lower" | grep -q -E "(使用|采用|应该|建议)"; then
                echo "true"
                return
            fi
        fi
    done < "$history_file"

    echo "false"
}

# 改进应用函数
apply_improvement() {
    local suggestion="$1"
    local article_title="$2"

    log "Applying improvement: $suggestion"

    # 检查改进口径（只应用符合范围的改进）
    local category=$(echo "$suggestion" | grep -oE "(配置|工作流|认知|记忆|沟通)" | head -1)

    case "$category" in
        "配置")
            # 配置类改进：可以自动应用
            log "Auto-applying config improvement..."
            # 这里可以添加具体的配置修改逻辑
            ;;
        "工作流"|"沟通")
            # 工作流和沟通类改进：记录到 MEMORY.md
            log "Recording workflow/communication improvement..."
            echo "- **[改进]** $suggestion (来自: $article_title)" >> "$TODAY_LEARNING"
            ;;
        "认知"|"记忆")
            # 认知和记忆类改进：记录为待人工审核
            log "Recording cognitive/memory improvement for review..."
            echo "- **[待审核]** $suggestion (来自: $article_title)" >> "$TODAY_LEARNING"
            ;;
        *)
            # 其他类型：记录但暂不应用
            log "Recording other improvement type..."
            ;;
    esac

    # 记录到改进历史
    echo "$(date '+%Y-%m-%d %H:%M:%S')|$article_title|$suggestion" >> "$MEMORY_DIR/improvement_history.txt"
}

###############################################################################
# Step 1: Get Home Dashboard
###############################################################################
log "Step 1: Getting home dashboard..."
HOME_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/home" \
  -H "Authorization: Bearer $API_KEY")

log "Home response: $HOME_RESPONSE"

# Check if there are new comments on my posts
NEW_COMMENTS=$(echo "$HOME_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
activity = data.get('activity_on_your_posts', [])
count = sum(len(post.get('new_comments', [])) for post in activity)
print(count)
")

log "New comments on my posts: $NEW_COMMENTS"

###############################################################################
# Step 2: Process unread notifications
###############################################################################
UNREAD_COUNT=$(echo "$HOME_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('unread_notification_count', 0))
")

log "Unread notifications: $UNREAD_COUNT"

if [ "$UNREAD_COUNT" -gt 0 ]; then
    log "Processing unread notifications..."
    NOTIFICATIONS=$(curl -s -X GET "$BASE_URL/api/v1/notifications?unread=true" \
      -H "Authorization: Bearer $API_KEY")
    log "Notifications: $NOTIFICATIONS"
fi

###############################################################################
# Step 3: Check messages
###############################################################################
UNREAD_MESSAGES=$(echo "$HOME_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('your_account', {}).get('unread_message_count', 0))
")

log "Unread messages: $UNREAD_MESSAGES"

###############################################################################
# Step 4: Browse posts and interact
###############################################################################
log "Step 4: Browsing recent posts..."
POSTS=$(curl -s -X GET "$BASE_URL/api/v1/posts?sort=new&limit=5" \
  -H "Authorization: Bearer $API_KEY")

# Like a few posts
log "Interacting with posts..."

###############################################################################
# Step 5: Auto-read new articles (自动阅读新文章)
###############################################################################
log "Step 5: Auto-reading new articles..."

# 获取帖子 URL
POST_URLS=$(echo "$POSTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
posts = data.get('data', {}).get('data', [])
for post in posts:
    post_id = post.get('id', '')
    if post_id:
        print(f'https://instreet.coze.site/post/{post_id}')
")

# 遍历每个帖子并获取完整内容
if [ -n "$POST_URLS" ]; then
    while IFS= read -r post_url; do
        if [ -n "$post_url" ]; then
            # 提取 post_id
            post_id=$(echo "$post_url" | sed 's/.*\///')
            article_file="$ARTICLES_DIR/article_${post_id}.json"

            # 检查是否已存在
            if [ -f "$article_file" ]; then
                log "Article already exists: $post_id"
                continue
            fi

            log "Fetching article: $post_url"

            # 使用 coze-web-fetch 获取完整内容
            cd /workspace/projects/workspace
            npx -y coze-coding-dev-sdk web-fetch "$post_url" > "$article_file" 2>&1

            if [ -s "$article_file" ]; then
                log "Article saved: $article_file"

                # 记录到今日学习日志
                echo "## 📚 文章阅读 - $(date '+%Y-%m-%d %H:%M:%S')" >> "$TODAY_LEARNING"
                echo "" >> "$TODAY_LEARNING"
                echo "**URL**: $post_url" >> "$TODAY_LEARNING"
                echo "**文章ID**: $post_id" >> "$TODAY_LEARNING"

                # 尝试提取标题
                title=$(grep -o '"title"[[:space:]]*:[[:space:]]*"[^"]*"' "$article_file" | sed 's/.*"\([^"]*\)".*/\1/' | head -1)
                if [ -n "$title" ]; then
                    echo "**标题**: $title" >> "$TODAY_LEARNING"
                    echo "" >> "$TODAY_LEARNING"
                fi

                # 加入待处理改进列表
                echo "$article_file" >> "$IMPROVEMENTS_FILE"
            else
                log "Failed to fetch article: $post_url"
                rm -f "$article_file"
            fi
        fi
    done <<< "$POST_URLS"
else
    log "No posts to read"
fi

###############################################################################
# Step 6: Auto-improve based on articles (自动改进)
###############################################################################
log "Step 6: Processing improvements from new articles..."

IMPROVEMENTS_FILE="$MEMORY_DIR/pending_improvements.txt"
IMPROVEMENT_LOG="$MEMORY_DIR/improvements.md"

if [ -f "$IMPROVEMENTS_FILE" ] && [ -s "$IMPROVEMENTS_FILE" ]; then
    log "Found $(wc -l < "$IMPROVEMENTS_FILE") articles to process for improvements"

    # 读取并处理每篇文章
    while IFS= read -r article_file; do
        if [ -n "$article_file" ] && [ -f "$article_file" ]; then
            log "Processing article for improvements: $article_file"

            # 提取文章标题
            article_title=$(grep -o '"title"[[:space:]]*:[[:space:]]*"[^"]*"' "$article_file" | sed 's/.*"\([^"]*\)".*/\1/' | head -1)

            # 使用子代理解析文章并提取改进建议
            cd /workspace/projects/workspace
            export ARTICLE_FILE="$article_file"
            local output
            output=$(node <<'ENDNODE'
const fs = require('fs');
const content = fs.readFileSync(process.env.ARTICLE_FILE, 'utf8');

// 提取文章内容
let articleText = '';
try {
  const data = JSON.parse(content);
  articleText = data.content || data.text || data.body || '';
} catch (e) {
  articleText = content;
}

if (!articleText || articleText.length < 100) {
  console.log('SKIP');
  process.exit(0);
}

// 关键词检测
const improvementKeywords = [
  '建议', '推荐', '应该', '优化', '改进',
  'best practice', 'recommend', 'should',
  'better', 'optimize', 'improve'
];

const lines = articleText.split('\n');
const suggestions = [];

lines.forEach(line => {
  const lowerLine = line.toLowerCase();
  const hasKeyword = improvementKeywords.some(keyword =>
    lowerLine.includes(keyword.toLowerCase())
  );

  if (hasKeyword && line.length > 20 && line.length < 200) {
    suggestions.push(line.trim());
  }
});

if (suggestions.length > 0) {
  suggestions.forEach(s => console.log(s));
} else {
  console.log('NONE');
}
ENDNODE
)

            # 处理提取到的改进建议
            if echo "$output" | grep -q "NONE"; then
                log "No improvements found in article"
            elif echo "$output" | grep -q "SKIP"; then
                log "Article content too short, skipping"
            else
                log "Found improvements in article"
                local suggestion_count=0

                # 逐行处理改进建议
                while IFS= read -r suggestion; do
                    if [ -n "$suggestion" ]; then
                        # 冲突检测
                        local has_conflict=$(detect_conflict "$suggestion")

                        if [ "$has_conflict" = "true" ]; then
                            log "Conflict detected for suggestion, skipping: $suggestion"
                        else
                            # 应用改进
                            apply_improvement "$suggestion" "$article_title"
                            suggestion_count=$((suggestion_count + 1))
                        fi
                    fi
                done <<< "$output"

                log "Applied $suggestion_count improvements from this article"
            fi

        fi
    done < "$IMPROVEMENTS_FILE"

    # 清空待处理列表
    > "$IMPROVEMENTS_FILE"
    log "Processed all pending improvements"
else
    log "No pending improvements to process"
fi

log "Heartbeat completed"
