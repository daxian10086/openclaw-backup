# 📦 新机器安装 OpenClaw 备份工具

## 方案1: 从 GitHub 克隆并安装（推荐）⭐

### 步骤1: 克隆备份仓库

```bash
# 克隆你的备份仓库
git clone https://github.com/daxian10086/openclaw-backup.git /tmp/openclaw-backup

# 查看仓库内容
ls -la /tmp/openclaw-backup/
```

### 步骤2: 复制脚本到本地

```bash
# 创建脚本目录（如果不存在）
mkdir -p /workspace/projects/scripts

# 复制备份脚本
cp /tmp/openclaw-backup/scripts/backup_config.sh /workspace/projects/scripts/
cp /tmp/openclaw-backup/scripts/restore_config.sh /workspace/projects/scripts/
cp /tmp/openclaw-backup/scripts/openclaw-backup /workspace/projects/scripts/

# 添加执行权限
chmod +x /workspace/projects/scripts/backup_config.sh
chmod +x /workspace/projects/scripts/restore_config.sh
chmod +x /workspace/projects/scripts/openclaw-backup
```

### 步骤3: 创建全局命令

```bash
# 创建符号链接
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup

# 验证安装
openclaw-backup help
```

### 步骤4: 恢复配置

```bash
# 恢复配置
openclaw-backup restore https://github.com/daxian10086/openclaw-backup.git
```

---

## 方案2: 直接恢复配置（最简单）⭐⭐

### 步骤1: 克隆备份仓库

```bash
# 克隆到临时目录
git clone https://github.com/daxian10086/openclaw-backup.git /tmp/openclaw-backup
```

### 步骤2: 恢复工作区

```bash
# 创建工作区目录（如果不存在）
mkdir -p /workspace/projects/workspace

# 复制工作区内容
cp -r /tmp/openclaw-backup/workspace/* /workspace/projects/workspace/

# 复制脚本
cp -r /tmp/openclaw-backup/scripts/* /workspace/projects/scripts/

# 复制 OpenClaw 配置
cp /tmp/openclaw-backup/openclaw-config/openclaw.json /workspace/projects/ 2>/dev/null || true
```

### 步骤3: 安装备份工具

```bash
# 复制主命令
cp /tmp/openclaw-backup/scripts/openclaw-backup /workspace/projects/scripts/

# 添加执行权限
chmod +x /workspace/projects/scripts/openclaw-backup

# 创建全局命令
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup

# 验证
openclaw-backup help
```

### 步骤4: 重启 Gateway

```bash
# 重启使配置生效
sh /workspace/projects/scripts/restart.sh
```

---

## 方案3: 手动恢复（如果命令行不可用）⭐⭐⭐

### 步骤1: 克隆仓库

```bash
git clone https://github.com/daxian10086/openclaw-backup.git /tmp/openclaw-backup
```

### 步骤2: 手动复制文件

```bash
# 复制核心配置文件
cp /tmp/openclaw-backup/workspace/SOUL.md /workspace/projects/workspace/
cp /tmp/openclaw-backup/workspace/MEMORY.md /workspace/projects/workspace/
cp /tmp/openclaw-backup/workspace/AGENTS.md /workspace/projects/workspace/
cp /tmp/openclaw-backup/workspace/TOOLS.md /workspace/projects/workspace/

# 复制记忆文件
cp -r /tmp/openclaw-backup/workspace/memory /workspace/projects/workspace/

# 复制脚本
cp -r /tmp/openclaw-backup/scripts /workspace/projects/

# 复制配置
cp /tmp/openclaw-backup/openclaw-config/openclaw.json /workspace/projects/

# 复制技能（如果需要）
cp -r /tmp/openclaw-backup/skills /workspace/projects/workspace/ 2>/dev/null || true
```

### 步骤3: 安装备份工具

```bash
# 添加执行权限
chmod +x /workspace/projects/scripts/openclaw-backup
chmod +x /workspace/projects/scripts/backup_config.sh
chmod +x /workspace/projects/scripts/restore_config.sh

# 创建全局命令
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup
```

### 步骤4: 验证并重启

```bash
# 验证安装
openclaw-backup help

# 重启 Gateway
sh /workspace/projects/scripts/restart.sh
```

---

## 快速一键脚本

如果你想一键完成，创建以下脚本：

```bash
#!/bin/bash
# 新机器一键恢复脚本

echo "开始从 GitHub 恢复配置..."

# 克隆仓库
git clone https://github.com/daxian10086/openclaw-backup.git /tmp/openclaw-backup

# 创建目录
mkdir -p /workspace/projects/workspace
mkdir -p /workspace/projects/scripts

# 恢复工作区
cp -r /tmp/openclaw-backup/workspace/* /workspace/projects/workspace/

# 恢复脚本
cp -r /tmp/openclaw-backup/scripts/* /workspace/projects/scripts/

# 恢复配置
cp /tmp/openclaw-backup/openclaw-config/openclaw.json /workspace/projects/ 2>/dev/null || true

# 安装备份工具
chmod +x /workspace/projects/scripts/openclaw-backup
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup

# 验证
echo "验证安装..."
openclaw-backup help

echo "恢复完成！需要重启 Gateway 使配置生效。"
echo "重启命令: sh /workspace/projects/scripts/restart.sh"
```

保存为 `restore.sh`，然后运行：

```bash
chmod +x restore.sh
./restore.sh
```

---

## 验证恢复

恢复后，运行以下命令验证：

```bash
# 查看备份状态
openclaw-backup status

# 查看核心文件
ls -la /workspace/projects/workspace/SOUL.md
ls -la /workspace/projects/workspace/MEMORY.md
```

---

## 常见问题

### Q: 找不到 openclaw-backup 命令？

**A**: 检查符号链接是否创建：

```bash
ls -la /usr/local/bin/openclaw-backup

# 如果不存在，创建它
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup
```

### Q: restore 命令不可用？

**A**: 确保所有脚本都已复制并有执行权限：

```bash
chmod +x /workspace/projects/scripts/backup_config.sh
chmod +x /workspace/projects/scripts/restore_config.sh
chmod +x /workspace/projects/scripts/openclaw-backup

# 重新验证
openclaw-backup help
```

### Q: 恢复后配置未生效？

**A**: 需要重启 Gateway：

```bash
sh /workspace/projects/scripts/restart.sh
```

---

**推荐**: 使用方案2（直接恢复配置）最简单！
