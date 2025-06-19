#!/usr/bin/env python3
"""
データの重複を調査するスクリプト
"""

import os
from pathlib import Path
from collections import defaultdict

def investigate_duplicates():
    """データの重複を調査する"""
    data_dir = Path('data')
    
    print("=== CSS10データセットの重複調査 ===\n")
    
    # 各アーカイブの構造を調査
    for archive_num in range(1, 11):
        archive_path = data_dir / f"archive ({archive_num})"
        if not archive_path.exists():
            continue
            
        print(f"--- archive ({archive_num}) ---")
        
        # サブディレクトリを取得
        subdirs = [d for d in archive_path.iterdir() if d.is_dir()]
        
        # 言語コードディレクトリを特定
        lang_dirs = []
        content_dirs = []
        
        for subdir in subdirs:
            if subdir.name in ['de', 'el', 'es', 'fi', 'fr', 'hu', 'ja', 'nl', 'ru', 'zh']:
                lang_dirs.append(subdir)
            else:
                content_dirs.append(subdir)
        
        print(f"言語ディレクトリ: {[d.name for d in lang_dirs]}")
        print(f"コンテンツディレクトリ: {[d.name for d in content_dirs]}")
        
        # 重複チェック
        if lang_dirs and content_dirs:
            print("  → 重複の可能性があります")
            
            # 詳細な重複チェック
            for content_dir in content_dirs:
                content_name = content_dir.name
                
                # 対応する言語ディレクトリ内の同じ名前のディレクトリを探す
                for lang_dir in lang_dirs:
                    lang_content_dir = lang_dir / content_name
                    if lang_content_dir.exists():
                        content_files = len(list(content_dir.glob('*.wav')))
                        lang_files = len(list(lang_content_dir.glob('*.wav')))
                        
                        print(f"    {content_name}:")
                        print(f"      {content_dir}: {content_files}ファイル")
                        print(f"      {lang_content_dir}: {lang_files}ファイル")
                        
                        if content_files == lang_files:
                            print(f"      → 同じファイル数のため重複の可能性が高い")
                        
                        # ファイルサイズの比較
                        content_size = sum(f.stat().st_size for f in content_dir.glob('*.wav'))
                        lang_size = sum(f.stat().st_size for f in lang_content_dir.glob('*.wav'))
                        
                        if content_size == lang_size:
                            print(f"      → 同じ総サイズのため重複の可能性が高い")
                        else:
                            print(f"      → サイズが異なるため異なるデータの可能性")
        
        print()

def check_transcript_duplicates():
    """transcript.txtの重複をチェック"""
    print("=== transcript.txtの重複チェック ===\n")
    
    data_dir = Path('data')
    
    for archive_num in range(1, 11):
        archive_path = data_dir / f"archive ({archive_num})"
        if not archive_path.exists():
            continue
            
        transcript_file = archive_path / 'transcript.txt'
        if transcript_file.exists():
            with open(transcript_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # ファイルパスの重複をチェック
            file_paths = []
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    file_paths.append(parts[0])
            
            unique_paths = set(file_paths)
            duplicate_count = len(file_paths) - len(unique_paths)
            
            print(f"archive ({archive_num}): {len(lines)}行, ユニークファイル: {len(unique_paths)}, 重複: {duplicate_count}")

def recommend_strategy():
    """推奨戦略を提案"""
    print("\n=== 推奨戦略 ===")
    print("1. 言語ディレクトリ（de/, ja/など）を優先的に使用")
    print("   理由: 言語が明確に分類されており、整理されている")
    print()
    print("2. ルートレベルのコンテンツディレクトリは除外")
    print("   理由: 言語ディレクトリと重複している")
    print()
    print("3. 変換スクリプトを修正して重複を回避")
    print("   理由: 同じデータを2回処理することを防ぐ")

if __name__ == '__main__':
    investigate_duplicates()
    check_transcript_duplicates()
    recommend_strategy() 