# OpenClaw 配置备份工具

一键备份和恢复你的 OpenClaw 配置（包括 SOUL.md、MEMORY.md、技能、脚本等）。

## 快速开始

### 1. 备份配置

```bash
# 方式1: 本地备份
openclaw-backup backup

# 方式2: 备份并推送到 GitHub
openclaw-backup backup-push
```

### 2. 推送到 GitHub

首次推送时，选择以下方式之一：

**方式1: 使用 GitHub CLI 自动创建**
```bash
gh repo create openclaw-backup --public --source=. --remote=origin --push
```

**方式2: 手动创建仓库**
```bash
# 1. 访问 https://github.com/new
# 2. 创建新仓库: openclaw-backup
# 3. 执行以下命令:
git remote add origin https://github.com/YOUR_USERNAME/openclaw-backup.git
git branch -M main
git push -u origin main
```

### 3. 恢复配置

```bash
# 在新机器上，从 GitHub 恢复
openclaw-backup restore https://github.com/username/openclaw-backup.git

# 或使用简短格式
openclaw-backup restore github:username/openclaw-backup
```

### 4. 查看状态

```bash
openclaw-backup status
```

## 备份内容

- ✅ 工作区配置 (`/workspace/projects/workspace`)
  - SOUL.md - 你的个性化配置
  - MEMORY.md - 长期记忆
  - AGENTS.md - 项目管理
  - TOOLS.md - 工具配置
  - memory/ - 记忆文件
  - scripts/ - 自定义脚本

- ✅ OpenClaw 配置
  - openclaw.json - 主配置文件

- ✅ 技能目录
  - ~/.openclaw/skills/ - 自定义技能

## 命令参考

### openclaw-backup backup

本地备份配置到 `/tmp/openclaw-backup`。

```bash
openclaw-backup backup
```

### openclaw-backup backup-push

备份并推送到 GitHub。如果尚未配置远程仓库，会提示你设置。

```bash
openclaw-backup backup-push
```

### openclaw-backup restore <repo-url>

从 GitHub 恢复配置。会自动备份当前配置，然后恢复新配置。

```bash
# 完整 URL
openclaw-backup restore https://github.com/username/openclaw-backup.git

# 简短格式
openclaw-backup restore github:username/openclaw-backup
```

### openclaw-backup status

查看备份状态和文件列表。

```bash
openclaw-backup status
```

## 配置位置

### 备份位置
- 本地备份: `/tmp/openclaw-backup`
- 旧配置备份: `/tmp/openclaw-config-backup-YYYYMMDD-HHMMSS`

### 脚本位置
- 主命令: `/workspace/projects/scripts/openclaw-backup`
- 备份脚本: `/workspace/projects/scripts/backup_config.sh`
- 恢复脚本: `/workspace/projects/scripts/restore_config.sh`

## 高级用法

### 修改仓库名称

编辑 `/workspace/projects/scripts/backup_config.sh`，修改以下行：

```bash
GITHUB_REPO="your-repo-name"
```

### 定期自动备份

添加到 crontab：

```bash
# 每天凌晨 2 点自动备份
0 2 * * * /workspace/projects/scripts/openclaw-backup backup >> /tmp/openclaw-backup.log 2>&1

# 每天凌晨 2 点自动备份并推送
0 2 * * * /workspace/projects/scripts/openclaw-backup backup-push >> /tmp/openclaw-backup.log 2>&1
```

### 只备份特定文件

编辑 `backup_config.sh`，修改复制逻辑：

```bash
# 只备份 SOUL.md 和 MEMORY.md
cp "$WORKSPACE/SOUL.md" "$BACKUP_DIR/"
cp "$WORKSPACE/MEMORY.md" "$BACKUP_DIR/"
```

## 安全提示

1. **GitHub 仓库设置为私有**（如果包含敏感信息）
2. **检查备份内容**，确保没有泄露敏感信息
3. **定期测试恢复**，确保备份可用
4. **保存好 GitHub Token**（如果使用自动推送）

## 故障排除

### 备份失败

1. 检查磁盘空间: `df -h`
2. 检查文件权限: `ls -la /workspace/projects/workspace`
3. 查看日志: `cat /tmp/openclaw-backup.log`

### 恢复失败

1. 确认 GitHub 仓库地址正确
2. 检查网络连接
3. 查看旧配置备份: `ls -la /tmp/openclaw-config-backup-*`

### 推送到 GitHub 失败

1. 确认 GitHub CLI 已安装: `gh --version`
2. 登录 GitHub: `gh auth login`
3. 检查权限: `gh auth status`

## 更新日志

### v1.0.0 (2026-03-26)
- ✅ 初始版本
- ✅ 支持备份和恢复
- ✅ 支持推送到 GitHub
- ✅ 一键命令行工具

## 反馈

如果遇到问题或有建议，请提交 Issue。

---

**记住**: 定期备份，确保你的配置安全！
