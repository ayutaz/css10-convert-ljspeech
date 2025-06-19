#!/usr/bin/env python3
"""
ロシア語WAVファイルをIEEE浮動小数点からPCMフォーマットに変換するスクリプト
"""

import os
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm

def convert_wav_format(input_file, output_file):
    """WAVファイルをIEEE浮動小数点からPCMに変換"""
    try:
        # ffmpegを使用してIEEE浮動小数点（32bit）からPCM（16bit）に変換
        cmd = [
            'ffmpeg', '-y',  # 上書き許可
            '-i', str(input_file),  # 入力ファイル
            '-acodec', 'pcm_s16le',  # 16bit PCM
            '-ar', '22050',  # サンプルレート 22050Hz
            '-ac', '1',  # モノラル
            str(output_file)  # 出力ファイル
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)

def verify_wav_header(wav_file):
    """WAVファイルのヘッダーを検証"""
    try:
        with open(wav_file, 'rb') as f:
            # WAVヘッダーを確認
            riff = f.read(4)
            if riff != b'RIFF':
                return False, "RIFFヘッダーが不正"
            
            f.seek(8)
            wave = f.read(4)
            if wave != b'WAVE':
                return False, "WAVEヘッダーが不正"
            
            # ファイルサイズを取得
            f.seek(0, 2)
            file_size = f.tell()
            
            return True, f"{file_size:,} バイト"
            
    except Exception as e:
        return False, str(e)

def main():
    print("=== ロシア語WAVファイルフォーマット変換 ===\n")
    
    wavs_dir = Path('raw/wavs')
    ru_files = list(wavs_dir.glob('ru_*.wav'))
    
    if not ru_files:
        print("ロシア語WAVファイルが見つかりません")
        return
    
    print(f"変換対象: {len(ru_files)}ファイル")
    
    # バックアップディレクトリを作成
    backup_dir = Path('backup_russian_wavs')
    backup_dir.mkdir(exist_ok=True)
    print(f"バックアップディレクトリ: {backup_dir}")
    
    # テスト変換（最初の1ファイル）
    print(f"\n=== テスト変換（1ファイル） ===")
    test_file = ru_files[0]
    test_backup = backup_dir / test_file.name
    test_output = wavs_dir / f"{test_file.stem}.test.wav"
    
    print(f"テストファイル: {test_file.name}")
    
    # 元ファイルをバックアップ
    shutil.copy2(test_file, test_backup)
    
    # テスト変換
    success, error = convert_wav_format(test_file, test_output)
    
    if success:
        # 元ファイルサイズと変換後ファイルサイズを比較
        original_size = test_file.stat().st_size
        converted_size = test_output.stat().st_size
        
        print(f"✅ 変換成功")
        print(f"元ファイルサイズ: {original_size:,} バイト")
        print(f"変換後ファイルサイズ: {converted_size:,} バイト")
        
        # 変換後の検証
        print(f"\n=== 変換後の検証 ===")
        is_valid, info = verify_wav_header(test_output)
        if is_valid:
            print(f"{test_output.name}: {info}")
            print("  ✅ WAVヘッダー正常")
        else:
            print(f"❌ 検証失敗: {info}")
        
        # テストファイルを削除
        test_output.unlink()
        
        print(f"\nテスト完了。本格的な変換を実行しますか？")
        response = input("本格的な変換を実行しますか？ (y/N): ").strip().lower()
        
        if response != 'y':
            print("変換をキャンセルしました")
            return
        
    else:
        print(f"❌ テスト変換失敗: {error}")
        return
    
    # 本格的な変換
    print(f"\n=== ロシア語WAVファイルフォーマット変換 ===")
    print(f"変換対象: {len(ru_files)}ファイル")
    print(f"バックアップディレクトリ: {backup_dir}")
    
    print(f"\n変換を開始します...")
    
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # プログレスバー付きで変換
    for wav_file in tqdm(ru_files, desc="変換中"):
        # バックアップファイルパス
        backup_file = backup_dir / wav_file.name
        
        # 元ファイルをバックアップ
        shutil.copy2(wav_file, backup_file)
        
        # 一時出力ファイル
        temp_output = wavs_dir / f"{wav_file.stem}.temp.wav"
        
        # 変換実行
        success, error = convert_wav_format(wav_file, temp_output)
        
        if success:
            # 変換成功時は元ファイルを置き換え
            wav_file.unlink()
            temp_output.rename(wav_file)
            success_count += 1
        else:
            # 変換失敗時はバックアップから復元
            if temp_output.exists():
                temp_output.unlink()
            shutil.copy2(backup_file, wav_file)
            failed_count += 1
            failed_files.append((wav_file.name, error))
    
    # 結果表示
    print(f"\n=== 変換結果 ===")
    print(f"成功: {success_count}ファイル")
    print(f"失敗: {failed_count}ファイル")
    
    if failed_files:
        print(f"\n失敗したファイル:")
        for file_name, error in failed_files[:10]:  # 最初の10個のみ表示
            print(f"  {file_name}: {error}")
        if len(failed_files) > 10:
            print(f"  ... 他 {len(failed_files) - 10}ファイル")
    
    # 変換後の検証
    print(f"\n=== 変換後の検証 ===")
    sample_files = list(wavs_dir.glob('ru_*.wav'))[:5]
    
    for wav_file in sample_files:
        is_valid, info = verify_wav_header(wav_file)
        if is_valid:
            print(f"{wav_file.name}: {info}")
            print(f"  ✅ WAVヘッダー正常")
        else:
            print(f"{wav_file.name}: ❌ {info}")

if __name__ == "__main__":
    main() 