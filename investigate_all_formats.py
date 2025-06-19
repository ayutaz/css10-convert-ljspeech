#!/usr/bin/env python3
"""
全言語のWAVファイルフォーマットを調査するスクリプト
"""

import os
import wave
import struct
from pathlib import Path
from collections import defaultdict

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
    print("=== 全言語WAVファイルフォーマット調査 ===\n")
    
    wavs_dir = Path('raw/wavs')
    wav_files = list(wavs_dir.glob('*.wav'))
    
    if not wav_files:
        print("WAVファイルが見つかりません")
        return
    
    print(f"調査対象: {len(wav_files)}ファイル")
    
    # 言語別に分類
    lang_files = defaultdict(list)
    for wav_file in wav_files:
        lang_code = wav_file.stem.split('_')[0]
        lang_files[lang_code].append(wav_file)
    
    print(f"\n=== 言語別ファイル数 ===")
    for lang_code in sorted(lang_files.keys()):
        print(f"{lang_code}: {len(lang_files[lang_code])}ファイル")
    
    # 各言語のサンプルファイルを詳細調査
    print(f"\n=== 各言語サンプルファイル詳細調査 ===")
    for lang_code in sorted(lang_files.keys()):
        print(f"\n--- {lang_code} ---")
        sample_file = lang_files[lang_code][0]
        print(f"サンプルファイル: {sample_file.name}")
        
        format_info = investigate_wav_format(sample_file)
        
        if 'error' in format_info:
            print(f"エラー: {format_info['error']}")
        else:
            print(f"オーディオフォーマット: {format_info['audio_format']}")
            print(f"チャンネル数: {format_info['num_channels']}")
            print(f"サンプルレート: {format_info['sample_rate']} Hz")
            print(f"ビット深度: {format_info['bits_per_sample']} bit")
            print(f"ファイルサイズ: {format_info['file_size']:,} バイト")
            
            # フォーマットの説明
            if format_info['audio_format'] == 1:
                print(f"フォーマット: PCM ✅")
            elif format_info['audio_format'] == 3:
                print(f"フォーマット: IEEE浮動小数点 ⚠️")
            else:
                print(f"フォーマット: その他 (コード: {format_info['audio_format']}) ❌")
    
    # 全ファイルのフォーマット分布を調査
    print(f"\n=== 全ファイルフォーマット分布調査 ===")
    lang_format_counts = defaultdict(lambda: defaultdict(int))
    lang_error_counts = defaultdict(int)
    
    for lang_code, files in lang_files.items():
        print(f"\n{lang_code}言語の調査中...")
        
        for i, wav_file in enumerate(files):
            if i % 1000 == 0 and i > 0:
                print(f"  {lang_code}: {i}/{len(files)}")
                
            format_info = investigate_wav_format(wav_file)
            
            if 'error' in format_info:
                lang_error_counts[lang_code] += 1
            else:
                audio_format = format_info['audio_format']
                lang_format_counts[lang_code][audio_format] += 1
    
    # 結果表示
    print(f"\n=== 調査結果サマリー ===")
    for lang_code in sorted(lang_files.keys()):
        print(f"\n{lang_code}:")
        total_files = len(lang_files[lang_code])
        error_count = lang_error_counts[lang_code]
        print(f"  総ファイル数: {total_files}")
        print(f"  エラー数: {error_count}")
        
        for audio_format, count in sorted(lang_format_counts[lang_code].items()):
            percentage = (count / total_files) * 100
            format_name = "PCM" if audio_format == 1 else "IEEE浮動小数点" if audio_format == 3 else f"その他({audio_format})"
            status = "✅" if audio_format == 1 else "⚠️" if audio_format == 3 else "❌"
            print(f"  フォーマット {audio_format} ({format_name}): {count}ファイル ({percentage:.1f}%) {status}")
    
    # 問題のある言語を特定
    print(f"\n=== 問題のある言語の特定 ===")
    problematic_langs = []
    
    for lang_code in sorted(lang_files.keys()):
        has_ieee = lang_format_counts[lang_code].get(3, 0) > 0
        has_other = any(fmt != 1 and fmt != 3 for fmt in lang_format_counts[lang_code].keys())
        has_errors = lang_error_counts[lang_code] > 0
        
        if has_ieee or has_other or has_errors:
            problematic_langs.append((lang_code, has_ieee, has_other, has_errors))
    
    if problematic_langs:
        print("以下の言語に問題があります:")
        for lang_code, has_ieee, has_other, has_errors in problematic_langs:
            issues = []
            if has_ieee:
                issues.append("IEEE浮動小数点フォーマット")
            if has_other:
                issues.append("その他のフォーマット")
            if has_errors:
                issues.append("読み込みエラー")
            print(f"  {lang_code}: {', '.join(issues)}")
    else:
        print("✅ 全ての言語がPCMフォーマットで問題ありません")

if __name__ == "__main__":
    main() 