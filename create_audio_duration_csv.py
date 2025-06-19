#!/usr/bin/env python3
"""
WAVファイルの音声長データをCSVファイルとして作成するスクリプト
"""

import os
import numpy as np
import struct
import csv
from pathlib import Path
from datetime import datetime

def read_wav_header(wav_file):
    """WAVファイルのヘッダー情報を読み込み"""
    try:
        with open(wav_file, 'rb') as f:
            riff = f.read(4)
            if riff != b'RIFF':
                return None
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            if wave != b'WAVE':
                return None
            
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
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
                elif chunk_id == b'data':
                    if 'sample_rate' in locals():
                        duration = chunk_size / (sample_rate * num_channels * (bits_per_sample // 8))
                        return {
                            'audio_format': audio_format,
                            'num_channels': num_channels,
                            'sample_rate': sample_rate,
                            'byte_rate': byte_rate,
                            'block_align': block_align,
                            'bits_per_sample': bits_per_sample,
                            'file_size': file_size,
                            'duration': duration
                        }
                    else:
                        f.seek(chunk_size, 1)
                else:
                    f.seek(chunk_size, 1)
            
            return None
            
    except Exception as e:
        return None

def get_audio_duration(wav_file):
    """WAVファイルの音声長を取得（秒）"""
    try:
        header_info = read_wav_header(wav_file)
        if header_info and 'duration' in header_info:
            return header_info['duration']
        else:
            header_info = read_wav_header(wav_file)
            if header_info:
                data_size = header_info['file_size'] - 44
                duration = data_size / header_info['byte_rate']
                return duration
            return None
    except Exception as e:
        return None

def create_audio_duration_csv():
    """音声長データをCSVファイルとして作成"""
    print("=== WAVファイル音声長データCSV作成 ===")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    wavs_dir = Path('raw/wavs')
    wav_files = list(wavs_dir.glob('*.wav'))
    
    if not wav_files:
        print("WAVファイルが見つかりません")
        return
    
    print(f"処理対象: {len(wav_files):,}ファイル")
    print("音声長を計算中...")
    
    # CSVファイルの準備
    csv_file = Path('raw/audio_durations.csv')
    csv_file.parent.mkdir(exist_ok=True)
    
    # 統計情報
    total_files = len(wav_files)
    processed_files = 0
    failed_files = 0
    durations = []
    lang_counts = {}
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # ヘッダー行
        writer.writerow(['file_id', 'duration_seconds', 'language'])
        
        # 各ファイルの処理
        for i, wav_file in enumerate(wav_files):
            if i % 1000 == 0:
                print(f"  進捗: {i:,}/{total_files:,}")
            
            # ファイルID（拡張子なしのファイル名）
            file_id = wav_file.stem
            
            # 言語コード
            language = wav_file.stem.split('_')[0]
            
            # 音声長を取得
            duration = get_audio_duration(wav_file)
            
            if duration is not None:
                # CSVに書き込み
                writer.writerow([file_id, f"{duration:.6f}", language])
                
                # 統計情報を更新
                processed_files += 1
                durations.append(duration)
                lang_counts[language] = lang_counts.get(language, 0) + 1
            else:
                failed_files += 1
                print(f"   警告: {wav_file.name}の音声長取得に失敗")
    
    # 結果サマリー
    print(f"\n=== 処理完了 ===")
    print(f"出力ファイル: {csv_file}")
    print(f"処理成功: {processed_files:,}ファイル")
    print(f"処理失敗: {failed_files:,}ファイル")
    print(f"成功率: {processed_files/total_files*100:.1f}%")
    
    if durations:
        durations = np.array(durations)
        print(f"\n📊 音声長統計:")
        print(f"   最小: {np.min(durations):.3f}秒")
        print(f"   最大: {np.max(durations):.3f}秒")
        print(f"   平均: {np.mean(durations):.3f}秒")
        print(f"   中央値: {np.median(durations):.3f}秒")
        
        print(f"\n🌍 言語別ファイル数:")
        for lang_code in sorted(lang_counts.keys()):
            print(f"   {lang_code}: {lang_counts[lang_code]:,}ファイル")
    
    # CSVファイルの内容確認
    print(f"\n📋 CSVファイル内容確認:")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"   ヘッダー: {header}")
        
        # 最初の5行を表示
        print(f"   最初の5行:")
        for i, row in enumerate(reader):
            if i < 5:
                print(f"     {row}")
            else:
                break
    
    print(f"\n✅ CSVファイル作成完了: {csv_file}")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    create_audio_duration_csv() 