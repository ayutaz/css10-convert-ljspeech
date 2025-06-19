#!/usr/bin/env python3
"""
変換されたファイルを元のIEEE浮動小数点フォーマットに復元するスクリプト
"""

import shutil
from pathlib import Path

def restore_from_backup(backup_dir, target_dir):
    """バックアップから元のファイルを復元"""
    backup_path = Path(backup_dir)
    target_path = Path(target_dir)
    
    if not backup_path.exists():
        print(f"バックアップディレクトリが見つかりません: {backup_dir}")
        return 0
    
    restored_count = 0
    backup_files = list(backup_path.glob('*.wav'))
    
    print(f"復元対象: {len(backup_files)}ファイル")
    
    for backup_file in backup_files:
        target_file = target_path / backup_file.name
        
        # バックアップファイルを復元
        shutil.copy2(backup_file, target_file)
        restored_count += 1
    
    return restored_count

def main():
    print("=== 元のIEEE浮動小数点フォーマットへの復元 ===\n")
    
    wavs_dir = Path('raw/wavs')
    
    # 中国語ファイルの復元
    print("=== 中国語ファイルの復元 ===")
    zh_restored = restore_from_backup('backup_chinese_wavs', wavs_dir)
    print(f"復元完了: {zh_restored}ファイル")
    
    # ロシア語ファイルの復元
    print("\n=== ロシア語ファイルの復元 ===")
    ru_restored = restore_from_backup('backup_russian_wavs', wavs_dir)
    print(f"復元完了: {ru_restored}ファイル")
    
    # その他の言語ファイルの復元（進行中の変換がある場合）
    print("\n=== その他の言語ファイルの復元 ===")
    all_ieee_restored = restore_from_backup('backup_all_ieee_wavs', wavs_dir)
    print(f"復元完了: {all_ieee_restored}ファイル")
    
    total_restored = zh_restored + ru_restored + all_ieee_restored
    print(f"\n=== 復元完了 ===")
    print(f"総復元ファイル数: {total_restored}ファイル")
    
    # 復元後の確認
    print(f"\n=== 復元後の確認 ===")
    wav_files = list(wavs_dir.glob('*.wav'))
    print(f"WAVファイル総数: {len(wav_files)}ファイル")
    
    # 言語別ファイル数
    lang_counts = {}
    for wav_file in wav_files:
        lang_code = wav_file.stem.split('_')[0]
        lang_counts[lang_code] = lang_counts.get(lang_code, 0) + 1
    
    print(f"\n言語別ファイル数:")
    for lang_code in sorted(lang_counts.keys()):
        print(f"  {lang_code}: {lang_counts[lang_code]}ファイル")

if __name__ == "__main__":
    main() 