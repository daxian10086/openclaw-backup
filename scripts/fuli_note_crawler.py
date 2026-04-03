#!/usr/bin/env python3
"""
复利笔记小程序爬虫
爬取所有选手的比赛数据
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

# 配置
BASE_URL = "https://www.fuyinkeji.top/notebook/pageNotebookByMark"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://servicewechat.com/wx0a728bff9c077f80/132/page-frame.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254181c) XWEB/19201",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 你的认证参数（需要从抓包获取）
OPENID = "oTRR46s228EaoK0oP8QqlJxPZwU4"
GAME_SESSION = "14"
SATOKEN = "b7665cc5-aa22-47b9-ae7d-8cfee538ac8d"  # 需要更新

DB_PATH = "/workspace/projects/scripts/fuli_note_data.db"


def get_headers() -> Dict:
    """获取请求头"""
    headers = HEADERS.copy()
    headers["Satoken"] = SATOKEN
    return headers


def fetch_page(page_num: int, page_size: int = 20) -> Optional[Dict]:
    """获取单页数据"""
    params = {
        "openId": OPENID,
        "pageNum": page_num,
        "pageSize": page_size,
        "approve": 1,
        "gameSession": GAME_SESSION,
    }
    
    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=get_headers(),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def parse_notebook_list(data: Dict) -> List[Dict]:
    """解析笔记本列表数据"""
    items = []
    if data and data.get("code") == 200:
        notebook_list = data.get("data", {}).get("list", [])
        for item in notebook_list:
            parsed = {
                "notebook_id": item.get("id"),
                "openid": item.get("openid"),
                "game_session": item.get("gameSession"),
                "game_name": item.get("gameName"),
                "title": item.get("title"),
                "content": item.get("content"),
                "notebook_date": item.get("notebookDate"),
                "create_time": item.get("createTime"),
                "like_num": item.get("likeNum"),
                "is_order": item.get("isOrder"),
            }
            
            # 解析交易数据
            trading_data = item.get("data", [])
            if trading_data:
                td = trading_data[0]
                parsed.update({
                    "total_assets": td.get("totalAssets"),
                    "today_profit_loss": td.get("todayProfitLoss"),
                    "stock_percent": td.get("stockPercent"),
                    "today_earning_rate": td.get("todayEarningRate"),
                    "total_earning_rate": td.get("totalEarningRate"),
                    "streak_status": td.get("streakStatus"),
                })
            
            # 解析收益日历
            calendar = item.get("inComeCalendarList", [])
            parsed["calendar_count"] = len(calendar)
            
            items.append(parsed)
    return items


def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 笔记本列表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id TEXT UNIQUE,
            openid TEXT,
            game_session TEXT,
            game_name TEXT,
            title TEXT,
            content TEXT,
            notebook_date TEXT,
            create_time TEXT,
            like_num INTEGER,
            is_order INTEGER,
            total_assets TEXT,
            today_profit_loss REAL,
            stock_percent REAL,
            today_earning_rate TEXT,
            total_earning_rate TEXT,
            streak_status TEXT,
            calendar_count INTEGER,
            crawled_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 收益日历
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id TEXT,
            openid TEXT,
            game_name TEXT,
            hold_date TEXT,
            today_earning_rate TEXT,
            total_earning_rate TEXT,
            penalty_type INTEGER,
            penalty_reason TEXT,
            FOREIGN KEY (notebook_id) REFERENCES notebooks(notebook_id)
        )
    """)
    
    conn.commit()
    return conn


def save_notebooks(conn: sqlite3.Connection, items: List[Dict]):
    """保存笔记本数据"""
    cursor = conn.cursor()
    for item in items:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO notebooks 
                (notebook_id, openid, game_session, game_name, title, content, 
                 notebook_date, create_time, like_num, is_order, total_assets,
                 today_profit_loss, stock_percent, today_earning_rate,
                 total_earning_rate, streak_status, calendar_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["notebook_id"],
                item["openid"],
                item["game_session"],
                item["game_name"],
                item["title"],
                item["content"],
                item["notebook_date"],
                item["create_time"],
                item["like_num"],
                item["is_order"],
                item.get("total_assets"),
                item.get("today_profit_loss"),
                item.get("stock_percent"),
                item.get("today_earning_rate"),
                item.get("total_earning_rate"),
                item.get("streak_status"),
                item.get("calendar_count"),
            ))
        except Exception as e:
            print(f"保存失败: {e}")
    conn.commit()


def crawl_all(max_pages: int = None, delay: float = 1.0):
    """爬取所有数据"""
    print("=" * 50)
    print("复利笔记爬虫启动")
    print("=" * 50)
    
    conn = init_database()
    
    # 先获取第一页，确定总页数
    print("\n[1/3] 获取总页数...")
    first_page = fetch_page(1, 20)
    if not first_page or first_page.get("code") != 200:
        print("获取数据失败，请检查 Satoken 是否有效")
        return
    
    total_pages = first_page.get("data", {}).get("totalPage", 1)
    total_count = first_page.get("data", {}).get("total", 0)
    print(f"总页数: {total_pages}, 总记录数: {total_count}")
    
    if max_pages:
        total_pages = min(total_pages, max_pages)
        print(f"限制爬取前 {total_pages} 页")
    
    all_items = []
    
    # 解析第一页
    items = parse_notebook_list(first_page)
    all_items.extend(items)
    print(f"第1页: 获取 {len(items)} 条数据")
    
    # 爬取剩余页面
    print(f"\n[2/3] 爬取剩余 {total_pages - 1} 页...")
    for page in range(2, total_pages + 1):
        time.sleep(delay)  # 延迟，避免请求过快
        
        page_data = fetch_page(page, 20)
        if page_data:
            items = parse_notebook_list(page_data)
            all_items.extend(items)
            print(f"第{page}页: 获取 {len(items)} 条数据")
        else:
            print(f"第{page}页: 获取失败，跳过")
        
        # 每10页保存一次
        if page % 10 == 0:
            save_notebooks(conn, all_items)
            all_items = []
            print(f"  -> 已保存前 {page} 页数据")
    
    # 保存剩余数据
    if all_items:
        save_notebooks(conn, all_items)
    
    # 统计
    print(f"\n[3/3] 统计结果:")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notebooks")
    total = cursor.fetchone()[0]
    print(f"  总记录数: {total}")
    
    cursor.execute("SELECT COUNT(DISTINCT openid) FROM notebooks")
    unique_users = cursor.fetchone()[0]
    print(f"  独立用户数: {unique_users}")
    
    cursor.execute("SELECT game_name, COUNT(*) as cnt FROM notebooks GROUP BY game_name ORDER BY cnt DESC LIMIT 10")
    top_users = cursor.fetchall()
    print("  Top 10 用户:")
    for name, cnt in top_users:
        print(f"    {name}: {cnt}条")
    
    conn.close()
    print("\n✅ 爬取完成!")


def export_to_json(output_path: str = "/workspace/projects/scripts/fuli_data.json"):
    """导出为JSON"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notebooks ORDER BY notebook_date DESC")
    columns = [desc[0] for desc in cursor.description]
    
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(columns, row)))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    conn.close()
    print(f"已导出到 {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--export":
            export_to_json()
        elif sys.argv[1] == "--help":
            print("用法:")
            print("  python fuli_note_crawler.py          爬取所有数据")
            print("  python fuli_note_crawler.py --export  导出为JSON")
            print("  python fuli_note_crawler.py --help   显示帮助")
    else:
        crawl_all()
