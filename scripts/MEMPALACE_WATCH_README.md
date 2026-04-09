# MemPalace 会话监听服务

自动监听 OpenClaw 会话文件变化，实时导入到 MemPalace 长期记忆库。

## 功能说明

- 实时监听 `/workspace/projects/agents/main/sessions/` 目录
- 自动将 JSONL 格式的会话文件转换为 Markdown
- 导入到 MemPalace 的 `openclaw_session` wing
- 避免重复导入，只处理新增内容

## 安装依赖

```bash
apt-get install -y fswatch
```

## 使用方法

### 启动监听服务

```bash
# 使用默认配置
./scripts/start_mempalace_watch.sh

# 指定会话目录和 wing 名称
./scripts/start_mempalace_watch.sh /path/to/sessions my_wing
```

### 查看日志

```bash
tail -f /tmp/mempalace_watch.log
```

### 停止监听服务

```bash
./scripts/stop_mempalace_watch.sh
```

## 手动导入会话

如果需要手动导入特定会话：

```bash
# 将会话文件转换为 Markdown
python3 /workspace/projects/scripts/convert_session.py /path/to/session.jsonl

# 导入到 MemPalace
mempalace mine /tmp/mempalace_import --mode convos --wing openclaw_session
```

## 文件说明

- `mempalace_watch.sh` - 核心监听脚本
- `start_mempalace_watch.sh` - 启动服务（后台运行）
- `stop_mempalace_watch.sh` - 停止服务
- `mempal_save_hook.sh` - 手动保存脚本

## 配置项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 会话目录 | `/workspace/projects/agents/main/sessions` | OpenClaw 会话文件存储目录 |
| 目标 Wing | `openclaw_session` | MemPalace 中的 wing 名称 |
| 日志文件 | `/tmp/mempalace_watch.log` | 服务运行日志 |
| PID 文件 | `/tmp/mempalace_watch.pid` | 进程 ID 文件 |

## 注意事项

1. 会话文件大小需大于 100 字节才会被处理
2. 基于文件大小避免重复导入
3. 转换后的临时文件存储在 `/tmp/mempalace_import/`
4. 服务会在后台持续运行，直到手动停止
