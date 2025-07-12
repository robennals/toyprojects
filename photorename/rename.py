import argparse
from pathlib import Path
import shutil
import pandas as pd
import pytesseract
import cv2
from PIL import Image, ImageOps
import pillow_heif
import numpy as np

def load_image(path: Path) -> Image.Image:
    """Load image handling JPEG/PNG/HEIF and correct orientation."""
    suffix = path.suffix.lower()
    if suffix in {'.heic', '.heif'}:
        heif_file = pillow_heif.read_heif(str(path))
        img = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data, 'raw')
    else:
        img = Image.open(path)
    return ImageOps.exif_transpose(img)

def detect_name(img: Image.Image, valid_names):
    """Return a matching name if found and whether any text was detected."""
    # OCR the entire image.  In practice badges may sit well below the face and
    # the simple face-based crop used previously often missed the text.
    text = pytesseract.image_to_string(img, config='--psm 6')
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch.isspace()).strip()
    normalized = "".join(ch.lower() for ch in cleaned if ch.isalnum())
    for name in valid_names:
        name_norm = "".join(ch.lower() for ch in name if ch.isalnum())
        if name_norm in normalized:
            return name, True
    return None, bool(cleaned)

CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
FACE_THRESHOLD = 20.0

def face_vector(img: Image.Image):
    array = np.array(img.convert('RGB'))
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    # OpenCV Haar cascade returns a list of faces; we only use the first
    faces = CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    face_img = gray[y:y+h, x:x+w]
    face_img = cv2.resize(face_img, (100, 100))
    return face_img.flatten() / 255.0

def save_jpeg(img: Image.Image, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert('RGB').save(dest, format='JPEG')

def parse_args():
    parser = argparse.ArgumentParser(
        description='Rename photos based on badge recognition')
    parser.add_argument('spreadsheet', help='CSV with column name')
    parser.add_argument('input_dir', help='Folder with photos')
    parser.add_argument('output_dir', help='Output folder')
    parser.add_argument('--unmatched_dir', default='unmatched',
                        help='Folder for unmatched images')
    return parser.parse_args()

def read_names(path: Path):
    df = pd.read_csv(path)
    return df['name'].dropna().tolist()

def list_images(folder: Path):
    return sorted(p for p in folder.iterdir() if p.is_file())

def find_matches(enc, start_index, images, names):
    """Look ahead up to five images for matching faces."""
    matches = []
    for j in range(start_index + 1, min(len(images), start_index + 6)):
        next_path = images[j]
        try:
            next_img = load_image(next_path)
        except Exception:
            continue
        next_enc = face_vector(next_img)
        if next_enc is None:
            continue
        distance = np.linalg.norm(enc - next_enc)
        if distance < FACE_THRESHOLD:
            next_name, _ = detect_name(next_img, names)
            if next_name:
                matches.append(('badge', next_path))
            else:
                matches.append(('photo', next_path))
    return matches

def save_badge(name: str, img: Image.Image, output_dir: Path, badge_counts: dict):
    count = badge_counts.get(name, 0) + 1
    badge_counts[name] = count
    if count == 1:
        dest = output_dir / f'{name}-badge.jpeg'
    else:
        dest = output_dir / f'{name}-badge-{count}.jpeg'
    save_jpeg(img, dest)
    return count

def copy_matches(name: str, matches, count: int, output_dir: Path, used: set):
    photo_num = 1
    for kind, path in matches:
        if kind == 'photo':
            dest = output_dir / f'{name}-{photo_num}.jpeg'
            save_jpeg(load_image(path), dest)
            used.add(path)
            photo_num += 1
        else:
            count += 1
            dest = output_dir / f'{name}-badge-{count}.jpeg'
            save_jpeg(load_image(path), dest)
            used.add(path)
    return count

def process_badge(img_path: Path, img: Image.Image, name: str, index: int,
                  images, names, output_dir, unmatched_dir, used, badge_counts,
                  assigned_names):
    # compute a simple face encoding from the badge image
    enc = face_vector(img)
    if enc is None:
        print(f'No face found in badge {img_path}')
        shutil.copy(img_path, unmatched_dir / img_path.name)
        used.add(img_path)
        return
    # look ahead for regular photos of the same person
    matches = find_matches(enc, index, images, names)
    count = save_badge(name, img, output_dir, badge_counts)
    used.add(img_path)
    count = copy_matches(name, matches, count, output_dir, used)
    badge_counts[name] = count
    assigned_names.add(name)

def match_photo(img_path: Path, img: Image.Image, index: int, images, names,
                output_dir, unmatched_dir, used, badge_counts):
    # try to associate a non-badge photo with a nearby badge image
    enc = face_vector(img)
    matched = False
    if enc is not None:
        # search both earlier and later images for a badge photo of the same person
        for j in range(max(0, index - 5), min(len(images), index + 6)):
            if j == index:
                continue
            other_path = images[j]
            try:
                other_img = load_image(other_path)
            except Exception:
                continue
            other_name, _ = detect_name(other_img, names)
            if not other_name:
                continue
            other_enc = face_vector(other_img)
            if other_enc is None:
                continue
            distance = np.linalg.norm(other_enc - enc)
            if distance < FACE_THRESHOLD:
                count = badge_counts.get(other_name, 1)
                dest = output_dir / f'{other_name}-{count}.jpeg'
                save_jpeg(img, dest)
                used.add(img_path)
                matched = True
                break
    if not matched:
        print(f'Unmatched {img_path.name}')
        shutil.copy(img_path, unmatched_dir / img_path.name)
        used.add(img_path)

def finalize_unmatched(images, used, unmatched_dir):
    """Copy any images we never processed to the unmatched directory."""
    for img_path in images:
        if img_path not in used:
            print(f'Unmatched {img_path.name}')
            shutil.copy(img_path, unmatched_dir / img_path.name)

def main():
    args = parse_args()
    names = read_names(Path(args.spreadsheet))

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    unmatched_dir = Path(args.unmatched_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    unmatched_dir.mkdir(parents=True, exist_ok=True)

    images = list_images(input_dir)
    used = set()
    badge_counts = {}
    assigned_names = set()

    for i, img_path in enumerate(images):
        if img_path in used:
            continue
        try:
            img = load_image(img_path)
        except Exception as e:
            print(f'Could not load {img_path}: {e}')
            continue

        name, has_text = detect_name(img, names)
        if name:
            process_badge(img_path, img, name, i, images, names,
                          output_dir, unmatched_dir, used, badge_counts,
                          assigned_names)
        elif has_text and len(set(names) - assigned_names) == 1:
            remaining = list(set(names) - assigned_names)[0]
            process_badge(img_path, img, remaining, i, images, names,
                          output_dir, unmatched_dir, used, badge_counts,
                          assigned_names)
        else:
            match_photo(img_path, img, i, images, names, output_dir,
                        unmatched_dir, used, badge_counts)

    finalize_unmatched(images, used, unmatched_dir)

if __name__ == '__main__':
    main()
