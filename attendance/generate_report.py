#!/usr/bin/env python3
"""
生成上报格式报表（独立脚本）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from attendance_core import (
    parse_xdz_roster,
    parse_attendance,
    process_xdz_data,
    generate_report_format,
    get_attendance_date_range,
)

# 配置
roster_path = 'mock_data/创新智成-西安东站-花名册-2026.4.xlsx'
att_files = ['mock_data/员工刷卡记录表4-1.xls', 'mock_data/员工刷卡记录表4-2.xls']
output_path = 'output/上报报表_0311-0410.xlsx'

# 解析
roster = parse_xdz_roster(roster_path)
att_df = parse_attendance(att_files)
salary_df, daily_df = process_xdz_data(att_df, roster)

print(f"考勤记录数: {len(daily_df)}")
print(f"有打卡员工数: {daily_df['姓名'].nunique()}")

# 生成上报报表
os.makedirs('output', exist_ok=True)
generate_report_format(
    daily_df=daily_df,
    roster_path=roster_path,
    output_path=output_path,
    attendance_paths=att_files,
)

print(f"\n✅ 完成! 输出文件: {output_path}")
