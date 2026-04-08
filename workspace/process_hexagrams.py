#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量识别64张周易卦象图片并存储到SQLite数据库
"""

import sqlite3
import subprocess
import os
import re

DB_PATH = '/tmp/hexagrams.db'
IMAGE_DIR = '/workspace/projects/workspace/zhouyi64'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS hexagrams (
      id INTEGER PRIMARY KEY,
      number INTEGER,
      name TEXT,
      symbol TEXT,
      upper_trigram TEXT,
      lower_trigram TEXT,
      hexagram_text TEXT,
      line1_text TEXT,
      line1_xiang TEXT,
      line2_text TEXT,
      line2_xiang TEXT,
      line3_text TEXT,
      line3_xiang TEXT,
      line4_text TEXT,
      line4_xiang TEXT,
      line5_text TEXT,
      line5_xiang TEXT,
      line6_text TEXT,
      line6_xiang TEXT
    )''')
    conn.commit()
    return conn

def ocr_image(image_path):
    """对单张图片进行OCR识别"""
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', 'chi_sim'],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout
    except Exception as e:
        print(f"OCR Error for {image_path}: {e}")
        return None

def extract_hexagram_info(ocr_text, number):
    """从OCR文本中提取卦象信息"""
    lines = ocr_text.split('\n')
    
    # 清理文本
    clean_lines = [re.sub(r'\[.*?\]', '', line).strip() for line in lines if line.strip()]
    full_text = '\n'.join(clean_lines)
    
    # 尝试提取卦名
    name = None
    # 根据序号推断卦名
    hexagram_names = {
        1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '讼', 7: '师', 8: '比',
        9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '谦',
        16: '豫', 17: '随', 18: '蛊', 19: '临', 20: '观', 21: '噬嗑', 22: '贲',
        23: '剥', 24: '复', 25: '无妄', 26: '大畜', 27: '颐', 28: '大过', 29: '坎',
        30: '离', 31: '咸', 32: '恒', 33: '遁', 34: '大壮', 35: '晋', 36: '明夷',
        37: '家人', 38: '睽', 39: '蹇', 40: '解', 41: '损', 42: '益', 43: '夬',
        44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井', 49: '革', 50: '鼎',
        51: '震', 52: '艮', 53: '渐', 54: '归妹', 55: '丰', 56: '旅', 57: '巽',
        58: '兑', 59: '涣', 60: '节', 61: '中孚', 62: '小过', 63: '既济', 64: '未济'
    }
    name = hexagram_names.get(number, f'卦{number}')
    
    # 提取卦象符号 - 简化处理
    symbol = '☰☰'  # 默认
    
    # 提取上下卦
    trigrams = {
        '乾': '☰', '坤': '☷', '坎': '☵', '离': '☲',
        '震': '☳', '艮': '☶', '巽': '☴', '兑': '☱'
    }
    
    # 根据卦名推断上下卦
    upper_lower = {
        '乾': ('☰', '☰'), '坤': ('☷', '☷'), '屯': ('☵', '☳'),
        '蒙': ('☶', '☵'), '需': ('☴', '☰'), '讼': ('☰', '☵'),
        '师': ('☵', '☳'), '比': ('☵', '☷'), '小畜': ('☴', '☰'),
        '履': ('☱', '☰'), '泰': ('☷', '☰'), '否': ('☰', '☷'),
        '同人': ('☰', '☲'), '大有': ('☲', '☰'), '谦': ('☶', '☳'),
        '豫': ('☳', '☷'), '随': ('☳', '☱'), '蛊': ('☶', '☴'),
        '临': ('☷', '☰'), '观': ('☰', '☷'), '噬嗑': ('☲', '☳'),
        '贲': ('☲', '☶'), '剥': ('☷', '☶'), '复': ('☳', '☷'),
        '无妄': ('☰', '☳'), '大畜': ('☰', '☶'), '颐': ('☳', '☶'),
        '大过': ('☱', '☴'), '坎': ('☵', '☵'), '离': ('☲', '☲'),
        '咸': ('☱', '☳'), '恒': ('☳', '☱'), '遁': ('☰', '☶'),
        '大壮': ('☰', '☳'), '晋': ('☲', '☷'), '明夷': ('☷', '☲'),
        '家人': ('☲', '☴'), '睽': ('☲', '☱'), '蹇': ('☶', '☵'),
        '解': ('☳', '☵'), '损': ('☶', '☱'), '益': ('☱', '☳'),
        '夬': ('☰', '☱'), '姤': ('☱', '☰'), '萃': ('☷', '☱'),
        '升': ('☷', '☳'), '困': ('☷', '☱'), '井': ('☵', '☳'),
        '革': ('☱', '☲'), '鼎': ('☲', '☱'), '震': ('☳', '☳'),
        '艮': ('☶', '☶'), '渐': ('☳', '☴'), '归妹': ('☱', '☳'),
        '丰': ('☳', '☲'), '旅': ('☲', '☶'), '巽': ('☴', '☴'),
        '兑': ('☱', '☱'), '涣': ('☴', '☵'), '节': ('☵', '☱'),
        '中孚': ('☱', '☴'), '小过': ('☶', '☳'), '既济': ('☵', '☲'),
        '未济': ('☲', '☵')
    }
    upper_trigram, lower_trigram = upper_lower.get(name, ('☰', '☰'))
    symbol = upper_trigram + lower_trigram
    
    # 提取卦辞 - 找到大哉乾元类似的句子
    hexagram_text = ''
    # 提取从卦名后到第一爻之前的文本
    # 简化处理 - 存储部分OCR文本
    lines = full_text.split('\n')
    hexagram_text_parts = []
    found_卦辞 = False
    
    for i, line in enumerate(lines):
        # 跳过卦名行
        if name in line and len(line) < 10:
            found_卦辞 = True
            continue
        if found_卦辞 and line.strip():
            # 检查是否到达爻辞区域
            if '九' in line or '初' in line or '上' in line:
                break
            if line.strip() and not line.startswith('['):
                hexagram_text_parts.append(line.strip())
    
    hexagram_text = ' '.join(hexagram_text_parts[:3])  # 取前几行作为卦辞
    
    # 提取爻辞
    line_data = {
        'line1_text': '', 'line1_xiang': '',
        'line2_text': '', 'line2_xiang': '',
        'line3_text': '', 'line3_xiang': '',
        'line4_text': '', 'line4_xiang': '',
        'line5_text': '', 'line5_xiang': '',
        'line6_text': '', 'line6_xiang': ''
    }
    
    # 解析爻辞
    # 匹配模式如: "初九。潜龙，勿用。" 或 "九二：见龙在田，利见大人"
    pattern = r'([初九][一二三四五六]|[上九])\s*[：:。]([^。]+)'
    matches = re.findall(pattern, full_text)
    
    # 象曰解析
    xiang_pattern = r'象[日曰][\s:：]*(.+)'
    xiang_matches = re.findall(xiang_pattern, full_text)
    
    # 简单映射 - 假设按顺序
    line_keys = ['line1_text', 'line2_text', 'line3_text', 'line4_text', 'line5_text', 'line6_text']
    xiang_keys = ['line1_xiang', 'line2_xiang', 'line3_xiang', 'line4_xiang', 'line5_xiang', 'line6_xiang']
    
    # 手动提取更精确的爻辞
    # 初九
    if '初九' in full_text:
        m = re.search(r'初九[。：:]([^上]+)', full_text)
        if m:
            line_data['line1_text'] = '初九：' + m.group(1).strip()
    
    # 九二
    if '九二' in full_text:
        m = re.search(r'九二[。：:]([^九]+)', full_text)
        if m:
            line_data['line2_text'] = '九二：' + m.group(1).strip()
    
    # 九三
    if '九三' in full_text:
        m = re.search(r'九三[。：:]([^九]+)', full_text)
        if m:
            line_data['line3_text'] = '九三：' + m.group(1).strip()
    
    # 九四
    if '九四' in full_text:
        m = re.search(r'九四[。：:]([^九]+)', full_text)
        if m:
            line_data['line4_text'] = '九四：' + m.group(1).strip()
    
    # 九五
    if '九五' in full_text:
        m = re.search(r'九五[。：:]([^上]+)', full_text)
        if m:
            line_data['line5_text'] = '九五：' + m.group(1).strip()
    
    # 上九
    if '上九' in full_text:
        m = re.search(r'上九[。：:](.+)', full_text)
        if m:
            line_data['line6_text'] = '上九：' + m.group(1).strip()
    
    # 提取象曰
    # 潜龙勿用，阳在下也
    xiang_map = {}
    for match in xiang_matches:
        if '潜龙' in full_text and '阳在' in match:
            xiang_map['初'] = match
        elif '见龙' in full_text and '德施' in match:
            xiang_map['二'] = match
        elif '终日乾乾' in full_text:
            xiang_map['三'] = match
        elif '或跃' in full_text:
            xiang_map['四'] = match
        elif '飞龙' in full_text and '大人' in match:
            xiang_map['五'] = match
        elif '亢龙' in full_text:
            xiang_map['上'] = match
    
    # 简化处理 - 使用OCR原始文本
    return {
        'number': number,
        'name': name,
        'symbol': symbol,
        'upper_trigram': upper_trigram,
        'lower_trigram': lower_trigram,
        'hexagram_text': full_text[:500] if full_text else '',  # 存储部分卦辞
        'line1_text': line_data['line1_text'],
        'line1_xiang': '',
        'line2_text': line_data['line2_text'],
        'line2_xiang': '',
        'line3_text': line_data['line3_text'],
        'line3_xiang': '',
        'line4_text': line_data['line4_text'],
        'line4_xiang': '',
        'line5_text': line_data['line5_text'],
        'line5_xiang': '',
        'line6_text': line_data['line6_text'],
        'line6_xiang': ''
    }

def save_to_db(conn, data):
    """保存数据到数据库"""
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO hexagrams (
      number, name, symbol, upper_trigram, lower_trigram,
      hexagram_text, line1_text, line1_xiang, line2_text, line2_xiang,
      line3_text, line3_xiang, line4_text, line4_xiang, line5_text, line5_xiang,
      line6_text, line6_xiang
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
      (data['number'], data['name'], data['symbol'], data['upper_trigram'], data['lower_trigram'],
       data['hexagram_text'], data['line1_text'], data['line1_xiang'], data['line2_text'], data['line2_xiang'],
       data['line3_text'], data['line3_xiang'], data['line4_text'], data['line4_xiang'], data['line5_text'], data['line5_xiang'],
       data['line6_text'], data['line6_xiang']))
    conn.commit()

def process_all_images():
    """处理所有64张图片"""
    conn = init_db()
    
    # 卦名列表
    hexagram_names = [
        '乾', '坤', '屯', '蒙', '需', '讼', '师', '比',
        '小畜', '履', '泰', '否', '同人', '大有', '谦', '豫',
        '随', '蛊', '临', '观', '噬嗑', '贲', '剥', '复',
        '无妄', '大畜', '颐', '大过', '坎', '离', '咸', '恒',
        '遁', '大壮', '晋', '明夷', '家人', '睽', '蹇', '解',
        '损', '益', '夬', '姤', '萃', '升', '困', '井',
        '革', '鼎', '震', '艮', '渐', '归妹', '丰', '旅',
        '巽', '兑', '涣', '节', '中孚', '小过', '既济', '未济'
    ]
    
    success_count = 0
    failed = []
    
    for i in range(1, 65):
        img_path = f'{IMAGE_DIR}/{i:02d}.jpg'
        if not os.path.exists(img_path):
            print(f'Image not found: {img_path}')
            failed.append(i)
            continue
            
        print(f'Processing {i:02d}.jpg ({hexagram_names[i-1]})...')
        
        # OCR
        ocr_text = ocr_image(img_path)
        if not ocr_text:
            print(f'  OCR failed for {i:02d}.jpg')
            failed.append(i)
            continue
        
        # 提取信息
        data = extract_hexagram_info(ocr_text, i)
        
        # 保存到数据库
        try:
            save_to_db(conn, data)
            success_count += 1
            print(f'  Saved: {data["name"]}')
        except Exception as e:
            print(f'  Database error: {e}')
            failed.append(i)
    
    conn.close()
    return success_count, failed

if __name__ == '__main__':
    print('Starting hexagram OCR and database insertion...')
    success, failed = process_all_images()
    print(f'\n=== Results ===')
    print(f'Successfully processed: {success}/64 images')
    if failed:
        print(f'Failed: {failed}')
    print(f'Database saved to: {DB_PATH}')
