#!/usr/bin/env python3
"""
元のデータセットと重複回避版を比較するスクリプト
"""

import os
from pathlib import Path
from collections import Counter

def analyze_original_script():
    """元のスクリプトの動作を分析"""
    print("=== 元のスクリプトの動作分析 ===")
    
    # 元のスクリプトの処理ロジックを再現
    data_dir = Path('data')
    
    all_files_processed = []
    lang_dir_files = []
    root_dir_files = []
    
    for archive_num in range(1, 11):
        archive_path = data_dir / f"archive ({archive_num})"
        if not archive_path.exists():
            continue
        
        lang_code = get_language_code(archive_num)
        transcript_file = archive_path / 'transcript.txt'
        
        if not transcript_file.exists():
            continue
        
        with open(transcript_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                file_path = parts[0]
                
                # 元のスクリプトの処理ロジック
                # 1. 言語ディレクトリを確認
                lang_subfolder_path = archive_path / lang_code / file_path
                if lang_subfolder_path.exists():
                    lang_dir_files.append(f"{lang_code}_{Path(file_path).stem}")
                    all_files_processed.append(f"{lang_code}_{Path(file_path).stem}")
                    continue
                
                # 2. ルートレベルを確認
                root_path = archive_path / file_path
                if root_path.exists():
                    root_dir_files.append(f"{lang_code}_{Path(file_path).stem}")
                    all_files_processed.append(f"{lang_code}_{Path(file_path).stem}")
    
    print(f"元のスクリプトで処理されたファイル:")
    print(f"  総数: {len(all_files_processed)}")
    print(f"  言語ディレクトリから: {len(lang_dir_files)}")
    print(f"  ルートディレクトリから: {len(root_dir_files)}")
    
    # 重複チェック
    counter = Counter(all_files_processed)
    duplicates = {k: v for k, v in counter.items() if v > 1}
    
    print(f"  重複ファイル数: {len(duplicates)}")
    if duplicates:
        print(f"  重複例: {list(duplicates.items())[:5]}")
    
    return all_files_processed

def analyze_no_duplicates_script():
    """重複回避版の動作を分析"""
    print("\n=== 重複回避版の動作分析 ===")
    
    data_dir = Path('data')
    
    all_files_processed = []
    lang_dir_files = []
    root_dir_files = []
    
    for archive_num in range(1, 11):
        archive_path = data_dir / f"archive ({archive_num})"
        if not archive_path.exists():
            continue
        
        lang_code = get_language_code(archive_num)
        transcript_file = archive_path / 'transcript.txt'
        
        if not transcript_file.exists():
            continue
        
        with open(transcript_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                file_path = parts[0]
                
                # 重複回避版の処理ロジック
                # 言語ディレクトリを優先的に確認
                lang_subfolder_path = archive_path / lang_code / file_path
                if lang_subfolder_path.exists():
                    lang_dir_files.append(f"{lang_code}_{Path(file_path).stem}")
                    all_files_processed.append(f"{lang_code}_{Path(file_path).stem}")
                    continue
                
                # 言語ディレクトリにない場合のみルートレベルを確認
                root_path = archive_path / file_path
                if root_path.exists():
                    root_dir_files.append(f"{lang_code}_{Path(file_path).stem}")
                    all_files_processed.append(f"{lang_code}_{Path(file_path).stem}")
    
    print(f"重複回避版で処理されたファイル:")
    print(f"  総数: {len(all_files_processed)}")
    print(f"  言語ディレクトリから: {len(lang_dir_files)}")
    print(f"  ルートディレクトリから: {len(root_dir_files)}")
    
    # 重複チェック
    counter = Counter(all_files_processed)
    duplicates = {k: v for k, v in counter.items() if v > 1}
    
    print(f"  重複ファイル数: {len(duplicates)}")
    if duplicates:
        print(f"  重複例: {list(duplicates.items())[:5]}")
    
    return all_files_processed

def get_language_code(archive_num):
    """アーカイブ番号から言語コードを取得"""
    mapping = {
        1: 'de', 2: 'el', 3: 'es', 4: 'fi', 5: 'fr',
        6: 'hu', 7: 'ja', 8: 'nl', 9: 'ru', 10: 'zh'
    }
    return mapping.get(archive_num, 'unknown')

def compare_results():
    """結果を比較"""
    print("\n=== 結果比較 ===")
    
    # 実際のファイル数を確認
    original_wavs = list(Path('raw/wavs').glob('*.wav'))
    no_dup_wavs = list(Path('raw_no_duplicates/wavs').glob('*.wav'))
    
    print(f"実際のファイル数:")
    print(f"  元のデータセット: {len(original_wavs)}")
    print(f"  重複回避版: {len(no_dup_wavs)}")
    print(f"  差分: {len(original_wavs) - len(no_dup_wavs)}")
    
    # ファイル名の比較
    original_names = {f.stem for f in original_wavs}
    no_dup_names = {f.stem for f in no_dup_wavs}
    
    print(f"\nファイル名の比較:")
    print(f"  元のデータセットのユニーク名: {len(original_names)}")
    print(f"  重複回避版のユニーク名: {len(no_dup_names)}")
    print(f"  共通: {len(original_names & no_dup_names)}")
    print(f"  元のみ: {len(original_names - no_dup_names)}")
    print(f"  重複回避版のみ: {len(no_dup_names - original_names)}")

if __name__ == '__main__':
    original_files = analyze_original_script()
    no_dup_files = analyze_no_duplicates_script()
    compare_results() 