#!/usr/bin/env python3
"""
修复64卦数据库中运势、财运、家庭、健康列的数据
"""

import sqlite3
import pandas as pd
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import re
import os

def clean_text(text):
    """清理文本，移除无用标签和符号"""
    if pd.isna(text) or text == '':
        return ''

    # 移除标签
    text = re.sub(r'卦辞\s*占断', '', text)
    text = re.sub(r'卦辞', '', text)
    text = re.sub(r'占断', '', text)
    text = re.sub(r'^运势\s*', '', text)
    text = re.sub(r'^财运\s*', '', text)
    text = re.sub(r'^家庭\s*', '', text)
    text = re.sub(r'^健康\s*', '', text)

    # 移除竖线符号
    text = text.replace('丨', '')

    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def extract_text_from_image(image_path, ocr):
    """从图片中提取文字"""
    if not os.path.exists(image_path):
        print(f"警告: 图片不存在 {image_path}")
        return ''

    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"警告: 无法读取图片 {image_path}")
            return ''

        # 使用OCR识别
        result, _ = ocr(img)

        # 提取所有文字
        text_list = [line[0] for line in result]
        full_text = '\n'.join(text_list)

        return full_text
    except Exception as e:
        print(f"错误: OCR识别失败 {image_path}: {e}")
        return ''

def extract_field_from_text(text, field_name):
    """从完整文本中提取特定字段"""
    patterns = {
        '运势': [r'运势[：:]\s*(.*?)(?=\s*财运[：:]|$)',
                 r'运势\s*(.*?)(?=\s*财运|$)',
                 r'(?:卦辞\s*)?占断\s*(.*?)(?=\s*财运|$)'],
        '财运': [r'财运[：:]\s*(.*?)(?=\s*家庭[：:]|$)',
                 r'财运\s*(.*?)(?=\s*家庭|$)',
                 r'(?:卦辞\s*)?占断\s*(.*?)(?=\s*家庭|$)'],
        '家庭': [r'家庭[：:]\s*(.*?)(?=\s*健康[：:]|$)',
                 r'家庭\s*(.*?)(?=\s*健康|$)',
                 r'(?:卦辞\s*)?占断\s*(.*?)(?=\s*健康|$)'],
        '健康': [r'健康[：:]\s*(.*?)$',
                 r'健康\s*(.*?)$',
                 r'(?:卦辞\s*)?占断\s*(.*?)$']
    }

    for pattern in patterns.get(field_name, []):
        match = re.search(pattern, text, re.DOTALL)
        if match:
            result = match.group(1).strip()
            # 清理结果
            result = clean_text(result)
            if result:  # 如果有内容
                return result

    return ''

def main():
    # 初始化OCR
    ocr = RapidOCR()

    # 读取数据库
    conn = sqlite3.connect('/tmp/hexagrams_v16.db')
    df = pd.read_sql_query("SELECT * FROM hexagrams", conn)

    print(f"开始处理64卦数据...")

    # 获取总卦行（爻位=0）
    total_lines = df[df['爻位'] == 0].copy()

    print(f"总卦行数: {len(total_lines)}")

    # 统计修复前的空值
    print(f"\n修复前空值统计:")
    print(f"运势列空值数: {total_lines['运势'].isna().sum() + (total_lines['运势'] == '').sum()}")
    print(f"财运列空值数: {total_lines['财运'].isna().sum() + (total_lines['财运'] == '').sum()}")
    print(f"家庭列空值数: {total_lines['家庭'].isna().sum() + (total_lines['家庭'] == '').sum()}")
    print(f"健康列空值数: {total_lines['健康'].isna().sum() + (total_lines['健康'] == '').sum()}")

    # 处理每个卦
    updated_count = 0
    for idx, row in total_lines.iterrows():
        gua_seq = int(row['卦序'])
        image_path = f"/workspace/projects/workspace/zhouyi64/{gua_seq:02d}.jpg"

        print(f"\n处理卦序 {gua_seq} - {row['卦名']}...")

        # 从图片提取文字
        full_text = extract_text_from_image(image_path, ocr)

        if not full_text:
            print(f"  警告: 无法从图片提取文字")
            continue

        print(f"  识别文字: {full_text[:200]}...")

        # 提取各个字段
        运势 = extract_field_from_text(full_text, '运势')
        财运 = extract_field_from_text(full_text, '财运')
        家庭 = extract_field_from_text(full_text, '家庭')
        健康 = extract_field_from_text(full_text, '健康')

        print(f"  提取结果:")
        print(f"    运势: {运势 if 运势 else '空'}")
        print(f"    财运: {财运 if 财运 else '空'}")
        print(f"    家庭: {家庭 if 家庭 else '空'}")
        print(f"    健康: {健康 if 健康 else '空'}")

        # 更新DataFrame
        if 运势:
            df.at[idx, '运势'] = 运势
        if 财运:
            df.at[idx, '财运'] = 财运
        if 家庭:
            df.at[idx, '家庭'] = 家庭
        if 健康:
            df.at[idx, '健康'] = 健康

        updated_count += 1

    # 统计修复后的空值
    print(f"\n\n修复后空值统计:")
    updated_total_lines = df[df['爻位'] == 0]
    print(f"运势列空值数: {updated_total_lines['运势'].isna().sum() + (updated_total_lines['运势'] == '').sum()}")
    print(f"财运列空值数: {updated_total_lines['财运'].isna().sum() + (updated_total_lines['财运'] == '').sum()}")
    print(f"家庭列空值数: {updated_total_lines['家庭'].isna().sum() + (updated_total_lines['家庭'] == '').sum()}")
    print(f"健康列空值数: {updated_total_lines['健康'].isna().sum() + (updated_total_lines['健康'] == '').sum()}")

    # 保存到新数据库
    new_conn = sqlite3.connect('/tmp/hexagrams_v17.db')
    df.to_sql('hexagrams', new_conn, if_exists='replace', index=False)
    new_conn.close()

    # 导出为Excel
    with pd.ExcelWriter('/tmp/64卦数据库_v17.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='64卦数据', index=False)

    conn.close()

    print(f"\n处理完成！")
    print(f"更新了 {updated_count} 个卦")
    print(f"新数据库: /tmp/hexagrams_v17.db")
    print(f"新Excel: /tmp/64卦数据库_v17.xlsx")

if __name__ == "__main__":
    main()
