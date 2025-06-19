#!/usr/bin/env python3
"""
変換結果を分析するスクリプト
"""

import os
from pathlib import Path
from collections import Counter

def analyze_results():
    """変換結果を分析する"""
    raw_dir = Path('raw')
    wavs_dir = raw_dir / 'wavs'
    metadata_file = raw_dir / 'metadata.csv'
    
    print("=== CSS10 to LJSpeech 変換結果分析 ===\n")
    
    # 音声ファイル数
    wav_files = list(wavs_dir.glob('*.wav'))
    print(f"総音声ファイル数: {len(wav_files):,}")
    
    # 言語別統計
    language_counts = Counter()
    total_duration = 0
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                filename = parts[0]
                lang_code = parts[1]  # 新しい形式: speaker=de → de
                text = parts[2]
                
                language_counts[lang_code] += 1
    
    print(f"\n=== 言語別統計 ===")
    total_files = sum(language_counts.values())
    
    for lang_code, count in sorted(language_counts.items()):
        percentage = (count / total_files) * 100
        print(f"{lang_code:2s}: {count:6,} ファイル ({percentage:5.1f}%)")
    
    print(f"\n合計: {total_files:,} ファイル")
    
    # ファイルサイズ統計
    total_size = 0
    for wav_file in wav_files:
        total_size += wav_file.stat().st_size
    
    total_size_gb = total_size / (1024**3)
    print(f"\n=== ファイルサイズ ===")
    print(f"総サイズ: {total_size_gb:.2f} GB")
    print(f"平均ファイルサイズ: {total_size / len(wav_files) / 1024:.1f} KB")
    
    # メタデータファイルサイズ
    metadata_size = metadata_file.stat().st_size
    print(f"メタデータファイルサイズ: {metadata_size / 1024:.1f} KB")
    
    # サンプル表示
    print(f"\n=== メタデータサンプル ===")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 3:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    print(f"  {parts[0]}|{parts[1]}|{parts[2][:50]}...")
            else:
                break

if __name__ == '__main__':
    analyze_results() 