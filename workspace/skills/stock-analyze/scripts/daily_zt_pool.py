#!/usr/bin/env python3
"""
每日涨停池采集脚本
运行时间：16:00 收盘后
数据保存：SQLite数据库
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
except ImportError:
    print("❌ 请先安装 akshare: pip install akshare")
    sys.exit(1)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        'data', 'stock_analysis.db')

def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 涨停池表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zt_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            pct_change REAL,
            price REAL,
            amount REAL,
            market_cap REAL,
            turnover_rate REAL,
            board_count INTEGER,
            industry TEXT,
            first_seal_time TEXT,
            last_seal_time TEXT,
            broken_count INTEGER,
            UNIQUE(date, code)
        )
    ''')
    
    # 情绪评分表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            total_zt INTEGER,
            zt_amount REAL,
            avg_pct REAL,
            emotion_level TEXT,
            score INTEGER
        )
    ''')
    
    conn.commit()
    return conn

def get_today_str():
    """获取今天的日期字符串"""
    return datetime.now().strftime('%Y%m%d')

def collect_zt_pool(date_str):
    """采集涨停池数据"""
    print(f"📊 正在采集 {date_str} 涨停池数据...")
    
    try:
        # 转换日期格式：20260402 -> 2026-04-02
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        df = ak.stock_zt_pool_em(date=formatted_date)
        
        if df is None or df.empty:
            print("⚠️ 今日无涨停数据")
            return None
        
        print(f"✅ 成功获取 {len(df)} 只涨停股")
        return df
        
    except Exception as e:
        print(f"❌ 获取涨停池失败: {e}")
        return None

def calculate_emotion(df):
    """计算市场情绪评分"""
    if df is None or df.empty:
        return None
    
    # 基础指标
    total_zt = len(df)
    zt_amount = df['成交额'].sum() if '成交额' in df.columns else 0
    avg_pct = df['涨跌幅'].mean() if '涨跌幅' in df.columns else 0
    
    # 情绪等级判断
    if total_zt >= 100:
        emotion = "高潮"
        score = 90
    elif total_zt >= 60:
        emotion = "活跃"
        score = 75
    elif total_zt >= 30:
        emotion = "平稳"
        score = 60
    elif total_zt >= 10:
        emotion = "低迷"
        score = 40
    else:
        emotion = "冰点"
        score = 20
    
    return {
        'total_zt': total_zt,
        'zt_amount': zt_amount,
        'avg_pct': avg_pct,
        'emotion_level': emotion,
        'score': score
    }

def save_to_db(conn, date_str, df, emotion):
    """保存数据到数据库"""
    cursor = conn.cursor()
    
    # 保存涨停池
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO zt_pool 
                (date, code, name, pct_change, price, amount, market_cap, 
                 turnover_rate, board_count, industry, first_seal_time, 
                 last_seal_time, broken_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date_str,
                row.get('代码', ''),
                row.get('名称', ''),
                row.get('涨跌幅', 0),
                row.get('最新价', 0),
                row.get('成交额', 0),
                row.get('流通市值', 0),
                row.get('换手率', 0),
                row.get('连板数', 0),
                row.get('所属行业', ''),
                row.get('首次封板时间', ''),
                row.get('最后封板时间', ''),
                row.get('炸板次数', 0),
            ))
        except Exception as e:
            print(f"⚠️ 插入失败 {row.get('代码')}: {e}")
    
    # 保存情绪评分
    if emotion:
        cursor.execute('''
            INSERT OR REPLACE INTO emotion_score 
            (date, total_zt, zt_amount, avg_pct, emotion_level, score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            date_str,
            emotion['total_zt'],
            emotion['zt_amount'],
            emotion['avg_pct'],
            emotion['emotion_level'],
            emotion['score']
        ))
    
    conn.commit()
    print(f"✅ 已保存 {len(df)} 只涨停股到数据库")

def main():
    print("=" * 50)
    print("📊 每日涨停池采集")
    print("=" * 50)
    
    # 获取日期
    date_str = get_today_str()
    print(f"📅 采集日期: {date_str}")
    
    # 初始化数据库
    conn = init_db()
    
    # 采集涨停池
    df = collect_zt_pool(date_str)
    
    # 计算情绪
    emotion = calculate_emotion(df)
    if emotion:
        print(f"\n📈 情绪评分: {emotion['score']} ({emotion['emotion_level']})")
        print(f"   涨停家数: {emotion['total_zt']}")
        print(f"   涨停成交: {emotion['zt_amount']/1e8:.2f}亿")
        print(f"   平均涨幅: {emotion['avg_pct']:.2f}%")
    
    # 保存数据
    if df is not None:
        save_to_db(conn, date_str, df, emotion)
    
    conn.close()
    print("\n✅ 采集完成！")

if __name__ == '__main__':
    main()
