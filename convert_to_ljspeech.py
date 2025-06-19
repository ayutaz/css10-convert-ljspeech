#!/usr/bin/env python3
"""
CSS10データセットをLJSpeechフォーマットに変換するスクリプト

使用方法:
    python convert_to_ljspeech.py

出力:
    raw/
        wavs/          # 音声ファイル
        metadata.csv   # メタデータファイル
"""

import os
import shutil
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import re

# 言語コードのマッピング
LANGUAGE_MAPPING = {
    'archive (1)': 'de',  # ドイツ語
    'archive (2)': 'el',  # ギリシャ語
    'archive (3)': 'es',  # スペイン語
    'archive (4)': 'fi',  # フィンランド語
    'archive (5)': 'fr',  # フランス語
    'archive (6)': 'hu',  # ハンガリー語
    'archive (7)': 'ja',  # 日本語
    'archive (8)': 'nl',  # オランダ語
    'archive (9)': 'ru',  # ロシア語
    'archive (10)': 'zh', # 中国語
}

def parse_transcript_line(line):
    """transcript.txtの1行をパースする"""
    parts = line.strip().split('|')
    if len(parts) >= 3:
        file_path = parts[0]
        text = parts[1]
        return file_path, text
    return None, None

def get_language_from_archive(archive_name):
    """アーカイブ名から言語コードを取得"""
    return LANGUAGE_MAPPING.get(archive_name, 'unknown')

def find_wav_file(base_path, file_path_from_transcript):
    """WAVファイルの実際の場所を探す"""
    # transcript.txtのファイルパスから実際のWAVファイルを探す
    possible_paths = [
        base_path / file_path_from_transcript,
        base_path / file_path_from_transcript.replace('/', '\\'),
    ]
    
    # 言語サブフォルダも確認
    lang_code = get_language_from_archive(base_path.name)
    if lang_code != 'unknown':
        lang_subfolder_paths = [
            base_path / lang_code / file_path_from_transcript,
            base_path / lang_code / file_path_from_transcript.replace('/', '\\'),
        ]
        possible_paths.extend(lang_subfolder_paths)
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def process_archive(archive_path, output_wavs_dir, metadata_rows):
    """1つのアーカイブを処理する"""
    archive_name = archive_path.name
    lang_code = get_language_from_archive(archive_name)
    
    if lang_code == 'unknown':
        print(f"警告: {archive_name}の言語コードが不明です")
        return metadata_rows
    
    transcript_file = archive_path / 'transcript.txt'
    if not transcript_file.exists():
        print(f"警告: {archive_path}にtranscript.txtが見つかりません")
        return metadata_rows
    
    print(f"処理中: {archive_name} ({lang_code})")
    
    # transcript.txtを読み込み
    with open(transcript_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed_count = 0
    skipped_count = 0
    
    for line in tqdm(lines, desc=f"{archive_name}"):
        file_path_from_transcript, text = parse_transcript_line(line)
        
        if not file_path_from_transcript or not text:
            continue
        
        # WAVファイルを探す
        wav_file = find_wav_file(archive_path, file_path_from_transcript)
        
        if not wav_file:
            skipped_count += 1
            continue
        
        # 新しいファイル名を生成
        original_basename = Path(file_path_from_transcript).stem
        new_basename = f"{lang_code}_{original_basename}"
        new_wav_path = output_wavs_dir / f"{new_basename}.wav"
        
        # 重複チェック
        if new_wav_path.exists():
            skipped_count += 1
            continue
        
        # WAVファイルをコピー
        try:
            shutil.copy2(wav_file, new_wav_path)
            
            # メタデータ行を追加（speaker=を削除して言語コードのみ）
            metadata_row = f"{new_basename}|{lang_code}|{text}"
            metadata_rows.append(metadata_row)
            
            processed_count += 1
            
        except Exception as e:
            print(f"エラー: {wav_file}のコピーに失敗: {e}")
            skipped_count += 1
    
    print(f"  - 処理済み: {processed_count}ファイル")
    print(f"  - スキップ: {skipped_count}ファイル")
    
    return metadata_rows

def main():
    """メイン処理"""
    data_dir = Path('data')
    output_dir = Path('raw')
    output_wavs_dir = output_dir / 'wavs'
    
    # 出力ディレクトリを作成
    output_wavs_dir.mkdir(parents=True, exist_ok=True)
    
    # アーカイブディレクトリを取得
    archive_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('archive')]
    archive_dirs.sort(key=lambda x: int(x.name.split()[1].strip('()')))
    
    print(f"見つかったアーカイブ: {len(archive_dirs)}個")
    for archive_dir in archive_dirs:
        print(f"  - {archive_dir.name}")
    
    # メタデータ行を格納するリスト
    metadata_rows = []
    
    # 各アーカイブを処理
    for archive_dir in archive_dirs:
        metadata_rows = process_archive(archive_dir, output_wavs_dir, metadata_rows)
    
    # メタデータファイルを書き込み
    metadata_file = output_dir / 'metadata.csv'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        for row in metadata_rows:
            f.write(row + '\n')
    
    # 結果を表示
    wav_count = len(list(output_wavs_dir.glob('*.wav')))
    print(f"\n変換完了!")
    print(f"音声ファイル数: {wav_count}")
    print(f"メタデータ行数: {len(metadata_rows)}")
    print(f"出力ディレクトリ: {output_dir}")

if __name__ == '__main__':
    main() 