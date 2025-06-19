#!/usr/bin/env python3
"""
中国語WAVファイルを標準PCMフォーマットに変換するスクリプト
"""

import os
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm

def convert_wav_format(input_file, output_file):
    """WAVファイルを標準PCMフォーマットに変換"""
    try:
        # ffmpegコマンドを構築
        # IEEE浮動小数点（フォーマット3）から標準PCM（フォーマット1）に変換
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-acodec', 'pcm_s16le',  # 16ビットPCM
            '-ar', '22050',          # サンプルレート22,050Hz
            '-ac', '1',              # モノラル
            '-y',                    # 上書き許可
            str(output_file)
        ]
        
        # 変換実行
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"エラー: {input_file.name}")
            print(f"  stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"エラー: {input_file.name} - {e}")
        return False

def backup_and_convert():
    """バックアップを作成して変換を実行"""
    print("=== 中国語WAVファイルフォーマット変換 ===\n")
    
    wavs_dir = Path('raw/wavs')
    
    # 中国語ファイルを取得
    chinese_files = list(wavs_dir.glob('zh_*.wav'))
    if not chinese_files:
        print("中国語ファイルが見つかりません")
        return
    
    print(f"変換対象: {len(chinese_files)}ファイル")
    
    # バックアップディレクトリを作成
    backup_dir = Path('backup_chinese_wavs')
    backup_dir.mkdir(exist_ok=True)
    
    print(f"バックアップディレクトリ: {backup_dir}")
    
    # 変換結果を記録
    success_count = 0
    failed_files = []
    
    # 変換実行
    print("\n変換を開始します...")
    for wav_file in tqdm(chinese_files, desc="変換中"):
        # バックアップを作成
        backup_file = backup_dir / wav_file.name
        shutil.copy2(wav_file, backup_file)
        
        # 一時ファイル名で変換
        temp_file = wav_file.with_suffix('.tmp.wav')
        
        # 変換実行
        if convert_wav_format(wav_file, temp_file):
            # 変換成功時は元ファイルを置き換え
            wav_file.unlink()
            temp_file.rename(wav_file)
            success_count += 1
        else:
            # 変換失敗時はバックアップから復元
            if temp_file.exists():
                temp_file.unlink()
            shutil.copy2(backup_file, wav_file)
            failed_files.append(wav_file.name)
    
    # 結果表示
    print(f"\n=== 変換結果 ===")
    print(f"成功: {success_count}ファイル")
    print(f"失敗: {len(failed_files)}ファイル")
    
    if failed_files:
        print(f"\n失敗したファイル:")
        for file_name in failed_files[:10]:  # 最初の10個のみ表示
            print(f"  {file_name}")
        if len(failed_files) > 10:
            print(f"  ... 他 {len(failed_files) - 10}ファイル")
    
    # 変換後の検証
    if success_count > 0:
        print(f"\n変換後の検証を実行中...")
        verify_conversion(chinese_files[:5])  # 最初の5ファイルを検証

def verify_conversion(sample_files):
    """変換後のファイルを検証"""
    print(f"\n=== 変換後の検証 ===")
    
    for wav_file in sample_files:
        try:
            # 簡易的な検証（ファイルサイズとヘッダー確認）
            file_size = wav_file.stat().st_size
            print(f"{wav_file.name}: {file_size:,} バイト")
            
            # ヘッダーを確認
            with open(wav_file, 'rb') as f:
                riff = f.read(4)
                if riff == b'RIFF':
                    f.read(4)  # サイズをスキップ
                    wave = f.read(4)
                    if wave == b'WAVE':
                        print(f"  ✅ WAVヘッダー正常")
                    else:
                        print(f"  ❌ WAVE識別子不正: {wave}")
                else:
                    print(f"  ❌ RIFFヘッダー不正: {riff}")
                    
        except Exception as e:
            print(f"  ❌ 検証エラー: {e}")

def test_conversion():
    """テスト用の変換（1ファイルのみ）"""
    print("=== テスト変換（1ファイル） ===\n")
    
    wavs_dir = Path('raw/wavs')
    chinese_files = list(wavs_dir.glob('zh_*.wav'))
    
    if not chinese_files:
        print("中国語ファイルが見つかりません")
        return
    
    test_file = chinese_files[0]
    print(f"テストファイル: {test_file.name}")
    
    # バックアップを作成
    backup_dir = Path('backup_chinese_wavs')
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / test_file.name
    shutil.copy2(test_file, backup_file)
    
    # 一時ファイルで変換テスト
    temp_file = test_file.with_suffix('.test.wav')
    
    if convert_wav_format(test_file, temp_file):
        print("✅ 変換成功")
        
        # 変換後のファイルサイズを比較
        original_size = test_file.stat().st_size
        converted_size = temp_file.stat().st_size
        print(f"元ファイルサイズ: {original_size:,} バイト")
        print(f"変換後ファイルサイズ: {converted_size:,} バイト")
        
        # 変換後のファイルを検証
        verify_conversion([temp_file])
        
        # テストファイルを削除
        temp_file.unlink()
        
        print("\nテスト完了。本格的な変換を実行しますか？")
        return True
    else:
        print("❌ 変換失敗")
        return False

if __name__ == '__main__':
    # まずテスト変換を実行
    if test_conversion():
        response = input("\n本格的な変換を実行しますか？ (y/N): ")
        if response.lower() == 'y':
            backup_and_convert()
        else:
            print("変換をキャンセルしました")
    else:
        print("テスト変換に失敗したため、本格的な変換は実行しません") 