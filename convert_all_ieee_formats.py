#!/usr/bin/env python3
"""
全てのIEEE浮動小数点フォーマットのWAVファイルを一括変換するスクリプト
"""

import os
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm
import struct

def investigate_wav_format(wav_file):
    """WAVファイルのフォーマットを調査"""
    try:
        with open(wav_file, 'rb') as f:
            # WAVヘッダーを読み込み
            riff_header = f.read(4)
            file_size = struct.unpack('<I', f.read(4))[0]
            wave_header = f.read(4)
            
            # fmtチャンクを探す
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                    
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    # フォーマット情報を読み込み
                    audio_format = struct.unpack('<H', f.read(2))[0]
                    return audio_format
                else:
                    # このチャンクをスキップ
                    f.seek(chunk_size, 1)
                    
    except Exception as e:
        return None

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
    print("=== 全IEEE浮動小数点WAVファイル一括変換 ===\n")
    
    wavs_dir = Path('raw/wavs')
    wav_files = list(wavs_dir.glob('*.wav'))
    
    if not wav_files:
        print("WAVファイルが見つかりません")
        return
    
    print(f"調査対象: {len(wav_files)}ファイル")
    
    # IEEE浮動小数点フォーマットのファイルを特定
    print(f"\n=== IEEE浮動小数点フォーマットファイルの特定 ===")
    ieee_files = []
    pcm_files = []
    other_files = []
    
    for wav_file in tqdm(wav_files, desc="フォーマット調査中"):
        audio_format = investigate_wav_format(wav_file)
        
        if audio_format == 3:
            ieee_files.append(wav_file)
        elif audio_format == 1:
            pcm_files.append(wav_file)
        else:
            other_files.append(wav_file)
    
    print(f"IEEE浮動小数点フォーマット: {len(ieee_files)}ファイル")
    print(f"PCMフォーマット: {len(pcm_files)}ファイル")
    print(f"その他フォーマット: {len(other_files)}ファイル")
    
    if not ieee_files:
        print("✅ 変換が必要なファイルはありません")
        return
    
    # 言語別に分類
    lang_ieee_files = {}
    for wav_file in ieee_files:
        lang_code = wav_file.stem.split('_')[0]
        if lang_code not in lang_ieee_files:
            lang_ieee_files[lang_code] = []
        lang_ieee_files[lang_code].append(wav_file)
    
    print(f"\n=== 言語別変換対象 ===")
    for lang_code in sorted(lang_ieee_files.keys()):
        print(f"{lang_code}: {len(lang_ieee_files[lang_code])}ファイル")
    
    # バックアップディレクトリを作成
    backup_dir = Path('backup_all_ieee_wavs')
    backup_dir.mkdir(exist_ok=True)
    print(f"\nバックアップディレクトリ: {backup_dir}")
    
    # テスト変換（最初の1ファイル）
    print(f"\n=== テスト変換（1ファイル） ===")
    test_file = ieee_files[0]
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
    print(f"\n=== 全IEEE浮動小数点WAVファイル一括変換 ===")
    print(f"変換対象: {len(ieee_files)}ファイル")
    print(f"バックアップディレクトリ: {backup_dir}")
    
    print(f"\n変換を開始します...")
    
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # プログレスバー付きで変換
    for wav_file in tqdm(ieee_files, desc="変換中"):
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
    sample_files = list(wavs_dir.glob('*.wav'))[:5]
    
    for wav_file in sample_files:
        is_valid, info = verify_wav_header(wav_file)
        if is_valid:
            print(f"{wav_file.name}: {info}")
            print(f"  ✅ WAVヘッダー正常")
        else:
            print(f"{wav_file.name}: ❌ {info}")

if __name__ == "__main__":
    main() 