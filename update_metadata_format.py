#!/usr/bin/env python3
"""
既存のメタデータファイルの形式を更新するスクリプト
speaker=de → de の形式に変更
"""

import os
from pathlib import Path

def update_metadata_format():
    """メタデータファイルの形式を更新する"""
    metadata_file = Path('raw/metadata.csv')
    backup_file = Path('raw/metadata_backup.csv')
    
    if not metadata_file.exists():
        print("メタデータファイルが見つかりません: raw/metadata.csv")
        return
    
    print("メタデータファイルの形式を更新中...")
    
    # バックアップを作成
    if backup_file.exists():
        backup_file.unlink()
    metadata_file.rename(backup_file)
    
    updated_rows = []
    updated_count = 0
    
    # ファイルを読み込んで形式を更新
    with open(backup_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                filename = parts[0]
                speaker_info = parts[1]
                text = parts[2]
                
                # speaker=de → de の形式に変更
                if speaker_info.startswith('speaker='):
                    lang_code = speaker_info.split('=')[1]
                    new_line = f"{filename}|{lang_code}|{text}"
                    updated_rows.append(new_line)
                    updated_count += 1
                else:
                    # 既に正しい形式の場合はそのまま
                    updated_rows.append(line.strip())
                    updated_count += 1
    
    # 新しいファイルを書き込み
    with open(metadata_file, 'w', encoding='utf-8') as f:
        for row in updated_rows:
            f.write(row + '\n')
    
    print(f"更新完了!")
    print(f"処理した行数: {updated_count}")
    print(f"バックアップファイル: {backup_file}")
    print(f"更新されたファイル: {metadata_file}")
    
    # サンプルを表示
    if updated_rows:
        print(f"\n更新後のサンプル:")
        for i, row in enumerate(updated_rows[:3]):
            print(f"  {i+1}: {row}")

if __name__ == '__main__':
    update_metadata_format() 