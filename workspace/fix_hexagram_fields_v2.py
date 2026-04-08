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

    # 移除竖线符号
    text = text.replace('丨', '')

    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def extract_total_gua_data(image_path, ocr):
    """从图片中提取总卦的运势、财运、家庭、健康数据"""

    if not os.path.exists(image_path):
        print(f"警告: 图片不存在 {image_path}")
        return {}

    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"警告: 无法读取图片 {image_path}")
            return {}

        # 使用OCR识别
        result = ocr(img)

        if not result or len(result) < 1:
            print(f"警告: OCR识别失败 {image_path}")
            return {}

        text_list = result[0]

        # 获取图片高度，用于判断总卦区域（底部区域）
        img_height = img.shape[0]

        # 提取底部区域（总卦区域，大概是图片高度的70%以下）
        bottom_region = []
        for item in text_list:
            if len(item) >= 3:
                coords = item[0]
                text = item[1]
                confidence = item[2]

                # 计算Y坐标的中心点
                y_center = (coords[0][1] + coords[2][1]) / 2

                # 如果在底部区域（图片高度的70%以下）
                if y_center > img_height * 0.7:
                    bottom_region.append({
                        'text': text,
                        'confidence': confidence,
                        'y': y_center,
                        'x': (coords[0][0] + coords[2][0]) / 2
                    })

        # 按Y坐标排序
        bottom_region.sort(key=lambda x: x['y'])

        # 提取运势、财运、家庭、健康
        result_data = {'运势': '', '财运': '', '家庭': '', '健康': ''}
        current_field = None
        current_content = []

        for item in bottom_region:
            text = item['text'].strip()

            # 识别字段名
            if text in ['运势', '财运', '家庭', '健康', '占断', '卦辞']:
                # 保存上一个字段的内容
                if current_field and current_field in result_data:
                    if current_content:
                        content = clean_text(''.join(current_content))
                        # 如果字段已有内容，追加
                        if result_data[current_field]:
                            result_data[current_field] += ' ' + content
                        else:
                            result_data[current_field] = content
                    current_content = []

                # 如果是运势、财运、家庭、健康，则更新当前字段
                if text in ['运势', '财运', '家庭', '健康']:
                    current_field = text
                # 如果是占断或卦辞，则忽略或将其作为当前字段的一部分
                else:
                    # 保持当前字段不变
                    pass
            else:
                # 收集内容
                if current_field:
                    current_content.append(text)

        # 保存最后一个字段的内容
        if current_field and current_field in result_data and current_content:
            content = clean_text(''.join(current_content))
            if result_data[current_field]:
                result_data[current_field] += ' ' + content
            else:
                result_data[current_field] = content

        return result_data

    except Exception as e:
        print(f"错误: 提取失败 {image_path}: {e}")
        return {}

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
    success_count = 0
    fail_count = 0

    for idx, row in total_lines.iterrows():
        gua_seq = int(row['卦序'])
        image_path = f"/workspace/projects/workspace/zhouyi64/{gua_seq:02d}.jpg"

        print(f"\n处理卦序 {gua_seq} - {row['卦名']}...")

        # 从图片提取数据
        data = extract_total_gua_data(image_path, ocr)

        if not data:
            print(f"  警告: 无法从图片提取数据")
            fail_count += 1
            continue

        success_count += 1

        print(f"  提取结果:")
        print(f"    运势: {data.get('运势', '空')}")
        print(f"    财运: {data.get('财运', '空')}")
        print(f"    家庭: {data.get('家庭', '空')}")
        print(f"    健康: {data.get('健康', '空')}")

        # 更新DataFrame（如果数据有效）
        if data.get('运势'):
            df.at[idx, '运势'] = data['运势']
            updated_count += 1
        if data.get('财运'):
            df.at[idx, '财运'] = data['财运']
            updated_count += 1
        if data.get('家庭'):
            df.at[idx, '家庭'] = data['家庭']
            updated_count += 1
        if data.get('健康'):
            df.at[idx, '健康'] = data['健康']
            updated_count += 1

    # 统计修复后的空值
    print(f"\n\n处理完成！")
    print(f"成功: {success_count}, 失败: {fail_count}")
    print(f"更新了 {updated_count} 个字段")

    print(f"\n修复后空值统计:")
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

    print(f"\n新数据库: /tmp/hexagrams_v17.db")
    print(f"新Excel: /tmp/64卦数据库_v17.xlsx")

if __name__ == "__main__":
    main()
