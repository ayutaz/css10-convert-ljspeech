#!/usr/bin/env python3
"""
CSVファイルから総音声時間を計算するスクリプト
"""

import csv
import numpy as np

def calculate_total_duration():
    """CSVファイルから総音声時間を計算"""
    csv_file = 'raw/audio_durations.csv'
    
    durations = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        
        for row in reader:
            if len(row) >= 2:
                duration = float(row[1])
                durations.append(duration)
    
    total_duration = sum(durations)
    
    print(f"=== 総音声時間計算 ===")
    print(f"ファイル数: {len(durations):,}ファイル")
    print(f"総音声時間: {total_duration:,.2f}秒")
    print(f"総音声時間: {total_duration/60:.2f}分")
    print(f"総音声時間: {total_duration/3600:.2f}時間")
    print(f"総音声時間: {total_duration/3600/24:.2f}日")
    
    # 言語別の合計時間も計算
    lang_durations = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        
        for row in reader:
            if len(row) >= 3:
                duration = float(row[1])
                language = row[2]
                
                if language not in lang_durations:
                    lang_durations[language] = []
                lang_durations[language].append(duration)
    
    print(f"\n=== 言語別音声時間 ===")
    for lang_code in sorted(lang_durations.keys()):
        lang_total = sum(lang_durations[lang_code])
        lang_count = len(lang_durations[lang_code])
        print(f"{lang_code}: {lang_total:,.2f}秒 ({lang_total/3600:.2f}時間) - {lang_count:,}ファイル")

if __name__ == "__main__":
    calculate_total_duration() 