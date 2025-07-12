#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description='Update photo column in CSV based on named photos')
    parser.add_argument('spreadsheet', help='Input CSV used by yearbook with column name')
    parser.add_argument('photo_dir', help='Directory with photos named like "Name-1.jpeg"')
    parser.add_argument('-o', '--output', default='updated.csv', help='Output CSV path')
    return parser.parse_args()


def collect_photos(photo_dir: Path):
    mapping = {}
    for path in photo_dir.iterdir():
        if not path.is_file():
            continue
        stem = path.stem
        if '-' in stem:
            name = stem.split('-', 1)[0]
        else:
            name = stem
        if name not in mapping:
            mapping[name] = path.name
    return mapping


def main():
    args = parse_args()
    df = pd.read_csv(args.spreadsheet)
    photos = collect_photos(Path(args.photo_dir))
    if 'photo' not in df.columns:
        df['photo'] = ''
    df['photo'] = df.apply(lambda row: photos.get(str(row['name']), row['photo']), axis=1)
    df.to_csv(args.output, index=False)
    print(f'Saved updated CSV to {args.output}')


if __name__ == '__main__':
    main()
