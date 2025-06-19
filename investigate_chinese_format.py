#!/usr/bin/env python3
"""
中国語WAVファイルのフォーマットを調査するスクリプト
"""

import os
import struct
from pathlib import Path

def investigate_wav_header(wav_file):
    """WAVファイルのヘッダーを詳細に調査"""
    try:
        with open(wav_file, 'rb') as f:
            print(f"\n=== {wav_file.name} の詳細分析 ===")
            
            # ファイルサイズ
            file_size = wav_file.stat().st_size
            print(f"ファイルサイズ: {file_size:,} バイト")
            
            # RIFFヘッダー
            riff = f.read(4)
            print(f"RIFF識別子: {riff}")
            if riff != b'RIFF':
                print("❌ RIFFヘッダーが不正")
                return False
            
            # ファイルサイズ（RIFFチャンクサイズ）
            riff_size = struct.unpack('<I', f.read(4))[0]
            print(f"RIFFチャンクサイズ: {riff_size:,} バイト")
            
            # WAVE識別子
            wave = f.read(4)
            print(f"WAVE識別子: {wave}")
            if wave != b'WAVE':
                print("❌ WAVE識別子が不正")
                return False
            
            # チャンクを順次読み込み
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                print(f"\nチャンク: {chunk_id} (サイズ: {chunk_size:,} バイト)")
                
                if chunk_id == b'fmt ':
                    # fmtチャンクの詳細
                    audio_format = struct.unpack('<H', f.read(2))[0]
                    num_channels = struct.unpack('<H', f.read(2))[0]
                    sample_rate = struct.unpack('<I', f.read(4))[0]
                    byte_rate = struct.unpack('<I', f.read(4))[0]
                    block_align = struct.unpack('<H', f.read(2))[0]
                    bits_per_sample = struct.unpack('<H', f.read(2))[0]
                    
                    print(f"  音声フォーマット: {audio_format}")
                    print(f"  チャンネル数: {num_channels}")
                    print(f"  サンプルレート: {sample_rate:,} Hz")
                    print(f"  バイトレート: {byte_rate:,} bytes/sec")
                    print(f"  ブロックアライメント: {block_align}")
                    print(f"  ビット深度: {bits_per_sample}")
                    
                    # 追加のfmt情報がある場合
                    if chunk_size > 16:
                        extra_size = chunk_size - 16
                        extra_data = f.read(extra_size)
                        print(f"  追加データ: {extra_size} バイト")
                        if extra_size >= 2:
                            extra_param_size = struct.unpack('<H', extra_data[:2])[0]
                            print(f"  追加パラメータサイズ: {extra_param_size}")
                    
                elif chunk_id == b'data':
                    # dataチャンク
                    print(f"  データサイズ: {chunk_size:,} バイト")
                    # データの最初の数バイトを表示
                    data_start = f.read(min(16, chunk_size))
                    print(f"  データ開始: {data_start.hex()}")
                    # 残りをスキップ
                    if chunk_size > 16:
                        f.read(chunk_size - 16)
                    
                else:
                    # その他のチャンク
                    chunk_data = f.read(chunk_size)
                    print(f"  データ: {chunk_data[:16].hex()}...")
            
            return True
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def compare_formats():
    """中国語と他の言語のフォーマットを比較"""
    print("=== 中国語ファイルフォーマット調査 ===\n")
    
    wavs_dir = Path('raw/wavs')
    
    # 中国語ファイルを取得
    chinese_files = list(wavs_dir.glob('zh_*.wav'))
    if not chinese_files:
        print("中国語ファイルが見つかりません")
        return
    
    # 他の言語ファイルを取得
    other_files = [f for f in wavs_dir.glob('*.wav') if not f.stem.startswith('zh_')]
    if not other_files:
        print("他の言語ファイルが見つかりません")
        return
    
    print(f"中国語ファイル数: {len(chinese_files)}")
    print(f"他の言語ファイル数: {len(other_files)}")
    
    # 中国語ファイルの詳細分析
    print(f"\n{'='*50}")
    print("中国語ファイルの詳細分析")
    print(f"{'='*50}")
    
    # 最初の中国語ファイルを詳細分析
    chinese_sample = chinese_files[0]
    investigate_wav_header(chinese_sample)
    
    # 他の言語ファイルとの比較
    print(f"\n{'='*50}")
    print("他の言語ファイルとの比較")
    print(f"{'='*50}")
    
    # 各言語から1つずつサンプルを取得
    languages = ['de', 'el', 'es', 'fi', 'fr', 'hu', 'ja', 'nl', 'ru']
    for lang in languages:
        lang_files = [f for f in other_files if f.stem.startswith(f'{lang}_')]
        if lang_files:
            sample_file = lang_files[0]
            print(f"\n--- {lang} (サンプル: {sample_file.name}) ---")
            investigate_wav_header(sample_file)

if __name__ == '__main__':
    compare_formats() 