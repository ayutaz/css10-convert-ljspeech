#!/usr/bin/env python3
"""
metadata.csvとwavsフォルダの整合性を確認するスクリプト
"""

import os
from pathlib import Path
from collections import Counter

def verify_consistency():
    """metadata.csvとwavsフォルダの整合性を確認"""
    print("=== metadata.csvとwavsフォルダの整合性確認 ===\n")
    
    # パス設定
    raw_dir = Path('raw')
    metadata_file = raw_dir / 'metadata.csv'
    wavs_dir = raw_dir / 'wavs'
    
    # ファイルの存在確認
    if not metadata_file.exists():
        print(f"エラー: {metadata_file}が見つかりません")
        return
    
    if not wavs_dir.exists():
        print(f"エラー: {wavs_dir}が見つかりません")
        return
    
    # metadata.csvからIDを読み込み
    print("1. metadata.csvからIDを読み込み中...")
    metadata_ids = set()
    metadata_lines = []
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 3:
                file_id = parts[0]
                metadata_ids.add(file_id)
                metadata_lines.append((line_num, file_id, line))
            else:
                print(f"警告: 行{line_num}のフォーマットが不正: {line}")
    
    print(f"  読み込み完了: {len(metadata_ids)}個のID")
    
    # wavsフォルダからファイル名を読み込み
    print("\n2. wavsフォルダからファイル名を読み込み中...")
    wav_files = list(wavs_dir.glob('*.wav'))
    wav_ids = {f.stem for f in wav_files}
    
    print(f"  読み込み完了: {len(wav_ids)}個のWAVファイル")
    
    # 整合性チェック
    print("\n3. 整合性チェック...")
    
    # metadataにあり、wavsにないファイル
    missing_wavs = metadata_ids - wav_ids
    # wavsにあり、metadataにないファイル
    missing_metadata = wav_ids - metadata_ids
    # 共通部分
    common = metadata_ids & wav_ids
    
    print(f"  共通ファイル数: {len(common)}")
    print(f"  metadataのみ（WAVファイル不足）: {len(missing_wavs)}")
    print(f"  wavsのみ（メタデータ不足）: {len(missing_metadata)}")
    
    # 詳細レポート
    if missing_wavs:
        print(f"\n4. WAVファイルが不足しているID（最初の10個）:")
        for i, missing_id in enumerate(sorted(missing_wavs)[:10]):
            print(f"  {i+1}: {missing_id}")
        if len(missing_wavs) > 10:
            print(f"  ... 他{len(missing_wavs) - 10}個")
    
    if missing_metadata:
        print(f"\n5. メタデータが不足しているWAVファイル（最初の10個）:")
        for i, missing_id in enumerate(sorted(missing_metadata)[:10]):
            print(f"  {i+1}: {missing_id}")
        if len(missing_metadata) > 10:
            print(f"  ... 他{len(missing_metadata) - 10}個")
    
    # 言語別の統計
    print(f"\n6. 言語別統計:")
    lang_stats = Counter()
    for file_id in common:
        lang_code = file_id.split('_')[0]
        lang_stats[lang_code] += 1
    
    for lang_code, count in sorted(lang_stats.items()):
        print(f"  {lang_code}: {count}ファイル")
    
    # 重複チェック
    print(f"\n7. 重複チェック:")
    metadata_counter = Counter()
    for line_num, file_id, line in metadata_lines:
        metadata_counter[file_id] += 1
    
    duplicates = {k: v for k, v in metadata_counter.items() if v > 1}
    if duplicates:
        print(f"  メタデータ内の重複: {len(duplicates)}個")
        for file_id, count in list(duplicates.items())[:5]:
            print(f"    {file_id}: {count}回")
    else:
        print(f"  メタデータ内の重複: なし")
    
    # 結果サマリー
    print(f"\n=== 結果サマリー ===")
    if len(missing_wavs) == 0 and len(missing_metadata) == 0:
        print(f"✅ 完全一致: metadata.csvとwavsフォルダが過不足なく一致しています")
    else:
        print(f"❌ 不一致: 以下の問題があります")
        if missing_wavs:
            print(f"   - {len(missing_wavs)}個のWAVファイルが不足")
        if missing_metadata:
            print(f"   - {len(missing_metadata)}個のメタデータが不足")
    
    print(f"総ファイル数: {len(common)}")
    print(f"言語数: {len(lang_stats)}")

def check_file_sizes():
    """ファイルサイズの確認"""
    print(f"\n=== ファイルサイズ確認 ===")
    
    wavs_dir = Path('raw/wavs')
    wav_files = list(wavs_dir.glob('*.wav'))
    
    if not wav_files:
        print("WAVファイルが見つかりません")
        return
    
    total_size = sum(f.stat().st_size for f in wav_files)
    avg_size = total_size / len(wav_files)
    
    print(f"WAVファイル数: {len(wav_files)}")
    print(f"総サイズ: {total_size / (1024**3):.2f} GB")
    print(f"平均ファイルサイズ: {avg_size / 1024:.1f} KB")
    
    # サイズ分布
    size_ranges = {
        "0-100KB": 0,
        "100KB-500KB": 0,
        "500KB-1MB": 0,
        "1MB以上": 0
    }
    
    for wav_file in wav_files:
        size = wav_file.stat().st_size
        if size < 100 * 1024:
            size_ranges["0-100KB"] += 1
        elif size < 500 * 1024:
            size_ranges["100KB-500KB"] += 1
        elif size < 1024 * 1024:
            size_ranges["500KB-1MB"] += 1
        else:
            size_ranges["1MB以上"] += 1
    
    print(f"\nファイルサイズ分布:")
    for range_name, count in size_ranges.items():
        percentage = (count / len(wav_files)) * 100
        print(f"  {range_name}: {count}ファイル ({percentage:.1f}%)")

if __name__ == '__main__':
    verify_consistency()
    check_file_sizes() 