# 自动版本号管理脚本使用说明

## 概述

`auto_update_version.py` 脚本可以自动递增小程序版本号，避免手动修改版本号的问题。

## 使用方法

### 方法1：直接运行脚本（推荐）

```bash
# 自动递增修订号（2.0.1 -> 2.0.2）
python3 /workspace/projects/workspace/auto_update_version.py
```

### 方法2：在更新流程中集成

在你的更新脚本中添加版本号更新步骤：

```bash
# 更新Excel数据
python3 update_data_from_excel.py

# 更新小程序数据
python3 generate_miniprogram_data.py

# 自动更新版本号
python3 /workspace/projects/workspace/auto_update_version.py

# 打包压缩
zip -r daxianzhouyi-miniprogram-v2.0.2.zip daxianzhouyi-miniprogram/
```

## 脚本功能

1. **自动读取当前版本号**
   - 从 `project.config.json` 读取当前版本
   - 支持格式：主版本.次版本.修订号（如 2.0.1）

2. **自动递增版本号**
   - 默认递增修订号（2.0.1 → 2.0.2）
   - 每次运行都会递增

3. **批量更新配置文件**
   - ✅ `project.config.json`
   - ✅ `app.json`
   - ✅ `VERSION.md`

4. **自动更新日期**
   - 自动更新 `versionDate` 为当前日期（YYYY-MM-DD）
   - 在 VERSION.md 中记录更新日期

## 版本号规则

- **格式**：主版本.次版本.修订号
- **示例**：
  - 2.0.1 → 2.0.2（修订号+1）
  - 2.0.9 → 2.1.0（次版本+1，修订号重置为0）
  - 2.9.9 → 3.0.0（主版本+1，次版本和修订号重置为0）

## 修改版本号类型（进阶）

如需递增不同级别的版本号，可以修改脚本中的 `increment_version` 函数：

```python
def increment_version(version):
    parts = version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    # 修改这里来决定递增哪个级别
    patch += 1  # 修订号（默认）
    # minor += 1  # 次版本
    # major += 1  # 主版本
    
    return f"{major}.{minor}.{patch}"
```

## 示例

**场景1：日常小更新**
```bash
python3 /workspace/projects/workspace/auto_update_version.py
# 结果：2.0.1 → 2.0.2
```

**场景2：功能更新**
```bash
# 修改脚本递增次版本
python3 /workspace/projects/workspace/auto_update_version.py
# 结果：2.0.5 → 2.1.0
```

**场景3：重大版本更新**
```bash
# 修改脚本递增主版本
python3 /workspace/projects/workspace/auto_update_version.py
# 结果：2.9.9 → 3.0.0
```

## 注意事项

1. ⚠️ 每次运行都会递增版本号
2. ⚠️ 建议只在发布新版本时运行此脚本
3. ⚠️ 脚本会覆盖所有相关配置文件中的版本号
4. ⚠️ 建议在更新数据前先运行，这样生成的压缩包版本号就是最新的

## 集成到工作流程

推荐的工作流程：

```bash
# 1. 更新Excel数据
python3 update_excel_data.py

# 2. 自动更新版本号
python3 /workspace/projects/workspace/auto_update_version.py

# 3. 生成小程序数据
python3 generate_miniprogram_data.py

# 4. 打包（版本号已经更新）
zip -r daxianzhouyi-miniprogram-$(date +%Y%m%d).zip daxianzhouyi-miniprogram/
```

这样每次发布的压缩包文件名都会包含版本号和日期：
- `daxianzhouyi-miniprogram-20260319.zip`
- `daxianzhouyi-miniprogram-20260320.zip`
- `daxianzhouyi-miniprogram-20260321.zip`
