#!/usr/bin/env python3
"""
WAVファイルの音声長を詳細に分析するスクリプト（簡易版）
"""

import os
import wave
import numpy as np
from pathlib import Path
from collections import defaultdict

def get_audio_duration(wav_file):
    """WAVファイルの音声長を取得（秒）"""
    try:
        with wave.open(str(wav_file), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"エラー: {wav_file}の読み込みに失敗: {e}")
        return None

def analyze_durations():
    """音声長を分析"""
    print("=== WAVファイル音声長分析 ===\n")
    
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
        if i % 5000 == 0:
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
    
    print(f"\n極値ファイルを特定中...")
    for wav_file in wav_files:
        duration = get_audio_duration(wav_file)
        if duration is not None:
            if abs(duration - min_duration) < 0.001:  # 浮動小数点の誤差を考慮
                min_file = wav_file
            if abs(duration - max_duration) < 0.001:
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
    
    # 分布の詳細
    print(f"\n=== 分布の詳細 ===")
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
        value = np.percentile(durations, p)
        print(f"  {p}パーセンタイル: {value:.3f}秒")
    
    # 時間範囲別のファイル数
    print(f"\n=== 時間範囲別ファイル数 ===")
    ranges = [
        (0, 5, "0-5秒"),
        (5, 10, "5-10秒"),
        (10, 15, "10-15秒"),
        (15, 20, "15-20秒"),
        (20, 30, "20-30秒"),
        (30, 60, "30-60秒"),
        (60, float('inf'), "60秒以上")
    ]
    
    for min_time, max_time, label in ranges:
        if max_time == float('inf'):
            count = np.sum(durations >= min_time)
        else:
            count = np.sum((durations >= min_time) & (durations < max_time))
        percentage = (count / len(durations)) * 100
        print(f"  {label}: {count}ファイル ({percentage:.1f}%)")
    
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

if __name__ == '__main__':
    stats = analyze_durations()
    if stats:
        print_summary(stats) 