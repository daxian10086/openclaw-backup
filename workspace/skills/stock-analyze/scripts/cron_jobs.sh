#!/bin/bash
# 股票分析系统定时任务配置
# 运行: crontab -e 添加以下任务

# ==================== 每日定时任务 ====================

# 16:00 收盘 - 采集涨停池
0 16 * * 1-5 cd /workspace/projects/workspace && python3 skills/stock-analyze/scripts/stock_system.py --mode=zt >> logs/zt_pool.log 2>&1

# 17:00 龙虎榜
0 17 * * 1-5 cd /workspace/projects/workspace && python3 skills/stock-analyze/scripts/stock_system.py --mode=lhb >> logs/lhb.log 2>&1

# 18:30 情绪评分
30 18 * * 1-5 cd /workspace/projects/workspace && python3 skills/stock-analyze/scripts/stock_system.py --mode=emotion >> logs/emotion.log 2>&1

# 08:30 早报
30 8 * * 1-5 cd /workspace/projects/workspace && python3 skills/stock-analyze/scripts/stock_system.py --mode=report >> logs/report.log 2>&1

# ==================== 安装说明 ====================
# 1. 运行 crontab -e
# 2. 添加上面的任务（去掉开头的#）
# 3. 保存退出
#
# 查看任务: crontab -l
# 删除任务: crontab -r
#
# 日志位置: /workspace/projects/workspace/skills/stock-analyze/logs/
