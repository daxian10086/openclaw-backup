# 🚀 OpenClaw 备份 - 推送到 GitHub

## 方案选择

由于 GitHub Token 权限限制，请选择以下方案之一：

## 方案1: 手动创建仓库（推荐）⭐

### 步骤1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名: `openclaw-backup`
3. 可见性: **Public**（公开）或 **Private**（私有）
4. **重要**: 不要勾选 "Add a README file"
5. **重要**: 不要勾选 "Add .gitignore"
6. **重要**: 不要勾选 "Choose a license"
7. 点击「Create repository」

### 步骤2: 推送备份

创建仓库后，运行以下命令：

```bash
cd /tmp/openclaw-backup
git push -u origin main
```

## 方案2: 升级 Token 权限

### 步骤1: 创建新 Token

1. 访问 https://github.com/settings/tokens
2. 点击「Generate new token」→「Generate new token (classic)」
3. Token 名称: `openclaw-backup`
4. 勾选权限:
   - ✅ **repo** (所有子权限)
   - ✅ **workflow** (可选，用于 GitHub Actions)
5. 点击「Generate token」
6. **复制 Token**（只会显示一次！）

### 步骤2: 使用新 Token 登录

```bash
# 先退出当前登录
gh auth logout

# 使用新 Token 登录
gh auth login
# 选择: GitHub.com
# 选择: HTTPS
# 选择: Login with a web browser
# 或选择: Paste an authentication token（粘贴刚才的 Token）
```

### 步骤3: 创建仓库并推送

```bash
# 创建仓库
gh repo create openclaw-backup --public

# 推送备份
cd /tmp/openclaw-backup
git push -u origin main
```

## 方案3: 使用 SSH Key（高级）

### 步骤1: 生成 SSH Key

```bash
# 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 GitHub
cat ~/.ssh/id_ed25519.pub
```

### 步骤2: 添加 SSH Key 到 GitHub

1. 复制上面的公钥
2. 访问 https://github.com/settings/keys
3. 点击「New SSH key」
4. 粘贴公钥
5. 点击「Add SSH key」

### 步骤3: 修改远程仓库 URL

```bash
cd /tmp/openclaw-backup
git remote set-url origin git@github.com:daxian10086/openclaw-backup.git

# 推送
git push -u origin main
```

## 快速命令总结

**方案1（推荐）**:
```bash
# 1. 访问 https://github.com/new 创建仓库
# 2. 推送
cd /tmp/openclaw-backup
git push -u origin main
```

**方案2**:
```bash
# 1. 创建新 Token（https://github.com/settings/tokens）
# 2. 重新登录
gh auth logout
gh auth login
# 3. 创建仓库并推送
gh repo create openclaw-backup --public
cd /tmp/openclaw-backup
git push -u origin main
```

**方案3**:
```bash
# 1. 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"
# 2. 添加到 GitHub（https://github.com/settings/keys）
# 3. 修改远程仓库 URL 并推送
cd /tmp/openclaw-backup
git remote set-url origin git@github.com:daxian10086/openclaw-backup.git
git push -u origin main
```

## 验证推送成功

推送成功后，访问以下地址查看：

```
https://github.com/daxian10086/openclaw-backup
```

## 下次更新

以后更新备份，只需运行：

```bash
openclaw-backup backup
cd /tmp/openclaw-backup
git add .
git commit -m "更新备份 - $(date '+%Y-%m-%d %H:%M:%S')"
git push
```

或使用一键命令：

```bash
openclaw-backup backup-push
```

---

**建议**: 使用方案1（手动创建仓库）最简单直接！
