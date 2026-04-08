# OpenClaw 备份工具 - 快速使用指南

## 一键命令

现在你可以使用一条命令完成所有备份/恢复操作！

### 📦 备份你的配置

```bash
openclaw-backup backup
```

**备份内容**：
- ✅ SOUL.md - 你的个性化配置
- ✅ MEMORY.md - 长期记忆
- ✅ AGENTS.md - 项目管理
- ✅ TOOLS.md - 工具配置
- ✅ 所有脚本和技能

### 🚀 推送到 GitHub

```bash
openclaw-backup backup-push
```

首次运行会提示你创建 GitHub 仓库。

### 📥 在新机器上恢复

```bash
# 从 GitHub 恢复
openclaw-backup restore https://github.com/你的用户名/openclaw-backup.git

# 或使用简短格式
openclaw-backup restore github:你的用户名/openclaw-backup
```

### 📊 查看状态

```bash
openclaw-backup status
```

## 完整工作流

### 场景1: 首次备份

```bash
# 1. 备份配置
openclaw-backup backup

# 2. 推送到 GitHub
openclaw-backup backup-push

# 3. 按提示创建 GitHub 仓库
gh repo create openclaw-backup --public --source=. --remote=origin --push
```

### 场景2: 更新备份

```bash
# 每次修改配置后，执行：
openclaw-backup backup-push
```

### 场景3: 换新机器

```bash
# 1. 安装 OpenClaw
# 2. 恢复配置
openclaw-backup restore https://github.com/你的用户名/openclaw-backup.git

# 3. 重启 Gateway
sh /workspace/projects/scripts/restart.sh
```

## 定时自动备份

每天凌晨 2 点自动备份：

```bash
# 添加到 crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/openclaw-backup backup >> /tmp/openclaw-backup.log 2>&1") | crontab -
```

## 备份位置

- **本地备份**: `/tmp/openclaw-backup`
- **旧配置备份**: `/tmp/openclaw-config-backup-YYYYMMDD-HHMMSS`

## 注意事项

⚠️ **重要提示**:
1. 恢复配置会覆盖当前配置
2. 恢复前会自动备份旧配置
3. 恢复后需要重启 Gateway
4. 建议定期测试恢复功能

## 快速测试

```bash
# 查看当前状态
openclaw-backup status

# 创建测试备份
openclaw-backup backup

# 查看备份内容
ls -la /tmp/openclaw-backup

# 查看备份报告
cat /tmp/openclaw-backup/backup-report.txt
```

---

**就这么简单！一条命令搞定备份和恢复！** 🎉
