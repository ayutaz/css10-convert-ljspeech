#!/usr/bin/env python3
"""
NumPyと標準ライブラリを使用してWAVファイルの音声長を詳細に分析するスクリプト
IEEE浮動小数点フォーマット対応
"""

import os
import numpy as np
import struct
from pathlib import Path
from collections import defaultdict

# matplotlibのインポートを試行（利用できない場合はスキップ）
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("matplotlibが利用できないため、分布図の作成をスキップします")

def read_wav_header(wav_file):
    """WAVファイルのヘッダー情報を読み込み"""
    try:
        with open(wav_file, 'rb') as f:
            # RIFFヘッダー
            riff = f.read(4)
            if riff != b'RIFF':
                return None
            
            # ファイルサイズ
            file_size = struct.unpack('<I', f.read(4))[0]
            
            # WAVEヘッダー
            wave = f.read(4)
            if wave != b'WAVE':
                return None
            
            # チャンクを探す
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    # フォーマット情報
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
                    # データチャンクのサイズから音声長を計算
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
                        # fmtチャンクがまだ見つかっていない場合
                        f.seek(chunk_size, 1)
                else:
                    # その他のチャンクをスキップ
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
            # データチャンクが見つからない場合、ファイルサイズから推定
            header_info = read_wav_header(wav_file)
            if header_info:
                # ファイルサイズから概算（ヘッダー部分を除く）
                data_size = header_info['file_size'] - 44  # 標準WAVヘッダーサイズ
                duration = data_size / header_info['byte_rate']
                return duration
            return None
    except Exception as e:
        print(f"エラー: {wav_file}の読み込みに失敗: {e}")
        return None

def analyze_durations():
    """音声長を分析"""
    print("=== NumPyを使用したWAVファイル音声長分析 ===\n")
    print("IEEE浮動小数点フォーマット対応\n")
    
    wavs_dir = Path('raw/wavs')
    wav_files = list(wavs_dir.glob('*.wav'))
    
    if not wav_files:
        print("WAVファイルが見つかりません")
        return
    
    print(f"分析対象: {len(wav_files)}ファイル")
    print("音声長を計算中...")
    
    # 音声長を取得
    durations = []
    lang_durations = defaultdict(list)
    failed_files = []
    
    for i, wav_file in enumerate(wav_files):
        if i % 1000 == 0:
            print(f"  進捗: {i}/{len(wav_files)}")
        
        duration = get_audio_duration(wav_file)
        if duration is not None:
            durations.append(duration)
            # 言語別に分類
            lang_code = wav_file.stem.split('_')[0]
            lang_durations[lang_code].append(duration)
        else:
            failed_files.append(wav_file)
    
    if not durations:
        print("有効な音声ファイルが見つかりませんでした")
        return
    
    # 統計計算
    durations = np.array(durations)
    
    print(f"\n=== 全体統計 ===")
    print(f"有効ファイル数: {len(durations)}")
    print(f"失敗ファイル数: {len(failed_files)}")
    
    # 基本統計
    min_duration = np.min(durations)
    max_duration = np.max(durations)
    mean_duration = np.mean(durations)
    median_duration = np.median(durations)
    
    print(f"\n基本統計:")
    print(f"  最小音声長: {min_duration:.3f}秒")
    print(f"  最大音声長: {max_duration:.3f}秒")
    print(f"  平均音声長: {mean_duration:.3f}秒")
    print(f"  中央値: {median_duration:.3f}秒")
    
    # 中央値から80%の範囲
    sorted_durations = np.sort(durations)
    total_files = len(sorted_durations)
    start_idx = int(total_files * 0.1)  # 下位10%
    end_idx = int(total_files * 0.9)    # 上位10%
    
    range_80_min = sorted_durations[start_idx]
    range_80_max = sorted_durations[end_idx]
    
    print(f"\n中央値から80%の範囲（上位・下位10%を除く）:")
    print(f"  最小値: {range_80_min:.3f}秒")
    print(f"  最大値: {range_80_max:.3f}秒")
    print(f"  範囲: {range_80_max - range_80_min:.3f}秒")
    
    # 最小・最大のファイルを特定
    min_file = None
    max_file = None
    
    for wav_file in wav_files:
        duration = get_audio_duration(wav_file)
        if duration is not None:
            if abs(duration - min_duration) < 0.001:  # 浮動小数点の比較
                min_file = wav_file
            if abs(duration - max_duration) < 0.001:  # 浮動小数点の比較
                max_file = wav_file
    
    print(f"\n=== 極値ファイル ===")
    if min_file:
        print(f"最短ファイル: {min_file.name}")
        print(f"  音声長: {min_duration:.3f}秒")
        print(f"  言語: {min_file.stem.split('_')[0]}")
    
    if max_file:
        print(f"最長ファイル: {max_file.name}")
        print(f"  音声長: {max_duration:.3f}秒")
        print(f"  言語: {max_file.stem.split('_')[0]}")
    
    # 言語別統計
    print(f"\n=== 言語別統計 ===")
    for lang_code in sorted(lang_durations.keys()):
        lang_durs = np.array(lang_durations[lang_code])
        print(f"\n{lang_code}:")
        print(f"  ファイル数: {len(lang_durs)}")
        print(f"  最小: {np.min(lang_durs):.3f}秒")
        print(f"  最大: {np.max(lang_durs):.3f}秒")
        print(f"  平均: {np.mean(lang_durs):.3f}秒")
        print(f"  中央値: {np.median(lang_durs):.3f}秒")
    
    # 分布の可視化
    if MATPLOTLIB_AVAILABLE:
        create_duration_histogram(durations, lang_durations)
    else:
        print("\n分布図の作成をスキップしました（matplotlibが利用できません）")
    
    return {
        'durations': durations,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'mean_duration': mean_duration,
        'median_duration': median_duration,
        'range_80_min': range_80_min,
        'range_80_max': range_80_max,
        'min_file': min_file,
        'max_file': max_file,
        'lang_durations': lang_durations
    }

def create_duration_histogram(durations, lang_durations):
    """音声長の分布を可視化"""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlibが利用できないため、分布図の作成をスキップしました")
        return
        
    plt.figure(figsize=(15, 10))
    
    # 全体の分布
    plt.subplot(2, 2, 1)
    plt.hist(durations, bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.xlabel('音声長 (秒)')
    plt.ylabel('ファイル数')
    plt.title('全体の音声長分布')
    plt.grid(True, alpha=0.3)
    
    # 言語別の箱ひげ図
    plt.subplot(2, 2, 2)
    lang_data = [lang_durations[lang] for lang in sorted(lang_durations.keys())]
    lang_labels = sorted(lang_durations.keys())
    plt.boxplot(lang_data, labels=lang_labels)
    plt.xlabel('言語コード')
    plt.ylabel('音声長 (秒)')
    plt.title('言語別音声長分布')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 言語別の平均音声長
    plt.subplot(2, 2, 3)
    lang_means = [np.mean(lang_durations[lang]) for lang in sorted(lang_durations.keys())]
    lang_counts = [len(lang_durations[lang]) for lang in sorted(lang_durations.keys())]
    
    bars = plt.bar(sorted(lang_durations.keys()), lang_means, alpha=0.7)
    plt.xlabel('言語コード')
    plt.ylabel('平均音声長 (秒)')
    plt.title('言語別平均音声長')
    
    # ファイル数を棒グラフの上に表示
    for i, (bar, count) in enumerate(zip(bars, lang_counts)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{count}', ha='center', va='bottom', fontsize=8)
    
    plt.grid(True, alpha=0.3)
    
    # 累積分布
    plt.subplot(2, 2, 4)
    sorted_durs = np.sort(durations)
    cumulative = np.arange(1, len(sorted_durs) + 1) / len(sorted_durs)
    plt.plot(sorted_durs, cumulative, linewidth=2)
    plt.xlabel('音声長 (秒)')
    plt.ylabel('累積確率')
    plt.title('音声長の累積分布')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('audio_duration_analysis_numpy.png', dpi=300, bbox_inches='tight')
    print(f"\n分布図を 'audio_duration_analysis_numpy.png' に保存しました")

def print_summary(stats):
    """分析結果のサマリーを表示"""
    print(f"\n=== 分析結果サマリー ===")
    print(f"📊 基本統計:")
    print(f"   最小音声長: {stats['min_duration']:.3f}秒")
    print(f"   最大音声長: {stats['max_duration']:.3f}秒")
    print(f"   平均音声長: {stats['mean_duration']:.3f}秒")
    print(f"   中央値: {stats['median_duration']:.3f}秒")
    
    print(f"\n📈 中央値から80%の範囲:")
    print(f"   最小値: {stats['range_80_min']:.3f}秒")
    print(f"   最大値: {stats['range_80_max']:.3f}秒")
    print(f"   範囲幅: {stats['range_80_max'] - stats['range_80_min']:.3f}秒")
    
    print(f"\n🎯 極値ファイル:")
    if stats['min_file']:
        print(f"   最短: {stats['min_file'].name} ({stats['min_duration']:.3f}秒)")
    if stats['max_file']:
        print(f"   最長: {stats['max_file'].name} ({stats['max_duration']:.3f}秒)")

if __name__ == "__main__":
    stats = analyze_durations()
    if stats:
        print_summary(stats) 