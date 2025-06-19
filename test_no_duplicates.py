#!/usr/bin/env python3
"""
重複回避版のテストスクリプト
"""

import os
import shutil
from pathlib import Path
from convert_to_ljspeech_no_duplicates import process_archive_no_duplicates

def test_single_archive():
    """1つのアーカイブでテスト"""
    # テスト用の出力ディレクトリ
    test_output_dir = Path('test_output_no_duplicates')
    test_wavs_dir = test_output_dir / 'wavs'
    test_wavs_dir.mkdir(parents=True, exist_ok=True)
    
    # テスト対象のアーカイブ（日本語）
    test_archive = Path('data/archive (7)')
    
    print("=== 重複回避版テスト ===")
    print(f"テスト対象: {test_archive}")
    
    # 処理実行
    metadata_rows = []
    metadata_rows = process_archive_no_duplicates(test_archive, test_wavs_dir, metadata_rows)
    
    # 結果確認
    wav_files = list(test_wavs_dir.glob('*.wav'))
    print(f"\n結果:")
    print(f"生成されたWAVファイル数: {len(wav_files)}")
    print(f"メタデータ行数: {len(metadata_rows)}")
    
    # 最初の数行を表示
    print(f"\n最初の5行のメタデータ:")
    for i, row in enumerate(metadata_rows[:5]):
        print(f"  {i+1}: {row}")
    
    # ファイル名の確認
    print(f"\n最初の5個のWAVファイル:")
    for i, wav_file in enumerate(wav_files[:5]):
        print(f"  {i+1}: {wav_file.name}")
    
    # 重複チェック
    file_names = [f.stem for f in wav_files]
    unique_names = set(file_names)
    print(f"\n重複チェック:")
    print(f"  総ファイル数: {len(file_names)}")
    print(f"  ユニークファイル数: {len(unique_names)}")
    print(f"  重複: {len(file_names) - len(unique_names)}")
    
    # クリーンアップ
    shutil.rmtree(test_output_dir)
    print(f"\nテスト完了。一時ファイルを削除しました。")

if __name__ == '__main__':
    test_single_archive() 