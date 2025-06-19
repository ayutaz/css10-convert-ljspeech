#!/usr/bin/env python3
"""
ロシア語WAVファイルのフォーマットを調査するスクリプト
"""

import os
import wave
import struct
from pathlib import Path

def investigate_wav_format(wav_file):
    """WAVファイルのフォーマットを詳細に調査"""
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
                    num_channels = struct.unpack('<H', f.read(2))[0]
                    sample_rate = struct.unpack('<I', f.read(4))[0]
                    byte_rate = struct.unpack('<I', f.read(4))[0]
                    block_align = struct.unpack('<H', f.read(2))[0]
                    bits_per_sample = struct.unpack('<H', f.read(2))[0]
                    
                    return {
                        'audio_format': audio_format,
                        'num_channels': num_channels,
                        'sample_rate': sample_rate,
                        'byte_rate': byte_rate,
                        'block_align': block_align,
                        'bits_per_sample': bits_per_sample,
                        'file_size': file_size
                    }
                else:
                    # このチャンクをスキップ
                    f.seek(chunk_size, 1)
                    
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=== ロシア語WAVファイルフォーマット調査 ===\n")
    
    wavs_dir = Path('raw/wavs')
    ru_files = list(wavs_dir.glob('ru_*.wav'))
    
    if not ru_files:
        print("ロシア語WAVファイルが見つかりません")
        return
    
    print(f"調査対象: {len(ru_files)}ファイル")
    
    # 最初の数ファイルを詳細調査
    sample_files = ru_files[:5]
    
    print(f"\n=== サンプルファイル詳細調査 ===")
    for i, wav_file in enumerate(sample_files):
        print(f"\n{i+1}. {wav_file.name}")
        format_info = investigate_wav_format(wav_file)
        
        if 'error' in format_info:
            print(f"   エラー: {format_info['error']}")
        else:
            print(f"   オーディオフォーマット: {format_info['audio_format']}")
            print(f"   チャンネル数: {format_info['num_channels']}")
            print(f"   サンプルレート: {format_info['sample_rate']} Hz")
            print(f"   ビット深度: {format_info['bits_per_sample']} bit")
            print(f"   ファイルサイズ: {format_info['file_size']:,} バイト")
            
            # フォーマットの説明
            if format_info['audio_format'] == 1:
                print(f"   フォーマット: PCM")
            elif format_info['audio_format'] == 3:
                print(f"   フォーマット: IEEE浮動小数点")
            else:
                print(f"   フォーマット: その他 (コード: {format_info['audio_format']})")
    
    # 全ファイルのフォーマット分布を調査
    print(f"\n=== 全ファイルフォーマット分布調査 ===")
    format_counts = {}
    error_count = 0
    
    for i, wav_file in enumerate(ru_files):
        if i % 1000 == 0:
            print(f"  進捗: {i}/{len(ru_files)}")
            
        format_info = investigate_wav_format(wav_file)
        
        if 'error' in format_info:
            error_count += 1
        else:
            audio_format = format_info['audio_format']
            format_counts[audio_format] = format_counts.get(audio_format, 0) + 1
    
    print(f"\n=== 調査結果 ===")
    print(f"総ファイル数: {len(ru_files)}")
    print(f"エラー数: {error_count}")
    
    for audio_format, count in sorted(format_counts.items()):
        percentage = (count / len(ru_files)) * 100
        format_name = "PCM" if audio_format == 1 else "IEEE浮動小数点" if audio_format == 3 else f"その他({audio_format})"
        print(f"フォーマット {audio_format} ({format_name}): {count}ファイル ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 