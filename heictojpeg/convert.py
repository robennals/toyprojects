#!/usr/bin/env python3
"""Convert HEIC images in a folder to JPEG, replacing the originals."""

import argparse
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

def convert_image(path: Path):
    """Convert a single HEIC image to JPEG and remove the original."""
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        dest = path.with_suffix('.jpeg')
        img.convert('RGB').save(dest, format='JPEG')
        path.unlink()
        print(f"Converted {path.name} -> {dest.name}")
    except Exception as e:
        print(f"Failed to convert {path}: {e}")


def convert_folder(folder: Path):
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in {'.heic', '.heif'}:
            convert_image(file)


def main():
    parser = argparse.ArgumentParser(description='Convert HEIC files to JPEG and remove the originals.')
    parser.add_argument('folder', help='Directory containing HEIC files')
    args = parser.parse_args()
    convert_folder(Path(args.folder))


if __name__ == '__main__':
    main()
