#!/usr/bin/env python3
"""
単一アーカイブのテスト実行スクリプト
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm

def parse_transcript_line(line):
    """transcript.txtの1行をパースする"""
    parts = line.strip().split('|')
    if len(parts) >= 3:
        file_path = parts[0]
        text = parts[1]
        return file_path, text
    return None, None

def find_wav_file(base_path, file_path_from_transcript):
    """WAVファイルの実際の場所を探す"""
    possible_paths = [
        base_path / file_path_from_transcript,
        base_path / file_path_from_transcript.replace('/', '\\'),
    ]
    
    # 言語サブフォルダも確認
    lang_subfolder_paths = [
        base_path / 'de' / file_path_from_transcript,
        base_path / 'de' / file_path_from_transcript.replace('/', '\\'),
    ]
    possible_paths.extend(lang_subfolder_paths)
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def test_archive_1():
    """archive (1)のテスト実行"""
    archive_path = Path('data/archive (1)')
    output_dir = Path('test_output')
    output_wavs_dir = output_dir / 'wavs'
    
    # 出力ディレクトリを作成
    output_wavs_dir.mkdir(parents=True, exist_ok=True)
    
    transcript_file = archive_path / 'transcript.txt'
    
    print(f"テスト実行: archive (1)")
    print(f"transcript.txt: {transcript_file}")
    
    # 最初の10行をテスト
    with open(transcript_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:10]
    
    metadata_rows = []
    processed_count = 0
    skipped_count = 0
    
    for i, line in enumerate(lines):
        print(f"\n行 {i+1}: {line.strip()}")
        
        file_path_from_transcript, text = parse_transcript_line(line)
        
        if not file_path_from_transcript or not text:
            print("  -> パース失敗")
            continue
        
        print(f"  ファイルパス: {file_path_from_transcript}")
        print(f"  テキスト: {text[:50]}...")
        
        # WAVファイルを探す
        wav_file = find_wav_file(archive_path, file_path_from_transcript)
        
        if not wav_file:
            print("  -> WAVファイルが見つかりません")
            skipped_count += 1
            continue
        
        print(f"  WAVファイル: {wav_file}")
        
        # 新しいファイル名を生成
        original_basename = Path(file_path_from_transcript).stem
        new_basename = f"de_{original_basename}"
        new_wav_path = output_wavs_dir / f"{new_basename}.wav"
        
        print(f"  新しいファイル名: {new_basename}")
        
        # WAVファイルをコピー
        try:
            shutil.copy2(wav_file, new_wav_path)
            
            # メタデータ行を追加
            metadata_row = f"{new_basename}|speaker=de|{text}"
            metadata_rows.append(metadata_row)
            
            processed_count += 1
            print("  -> 成功")
            
        except Exception as e:
            print(f"  -> エラー: {e}")
            skipped_count += 1
    
    # メタデータファイルを書き込み
    metadata_file = output_dir / 'metadata.csv'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        for row in metadata_rows:
            f.write(row + '\n')
    
    print(f"\nテスト結果:")
    print(f"処理済み: {processed_count}ファイル")
    print(f"スキップ: {skipped_count}ファイル")
    print(f"出力ディレクトリ: {output_dir}")

if __name__ == '__main__':
    test_archive_1() 