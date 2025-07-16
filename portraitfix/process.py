#!/usr/bin/env python3
"""Enhance portrait photos with optional color adjustment and background blur."""

import argparse
from pathlib import Path
import cv2
import numpy as np
import mediapipe as mp


def is_washed_out(image: np.ndarray, threshold: float = 40.0) -> bool:
    """Return True if the image appears low contrast."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray.std() < threshold


def background_is_blurred(
    image: np.ndarray,
    mask: np.ndarray | None = None,
    threshold: float = 50.0,
) -> bool:
    """Return True if the background has low sharpness."""
    if mask is None:
        with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as seg:
            result = seg.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        mask = result.segmentation_mask
    if mask is None:
        return False
    bg_mask = (mask <= 0.5).astype(np.uint8) * 255
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    background = cv2.bitwise_and(gray, gray, mask=bg_mask)
    return cv2.Laplacian(background, cv2.CV_64F).var() < threshold


def enhance_color(image: np.ndarray) -> np.ndarray:
    """Improve contrast using CLAHE on the L channel in LAB space."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab = cv2.merge((l2, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def blur_background(image: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Blur background while keeping the person sharp using selfie segmentation."""
    if mask is None:
        with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as segmenter:
            results = segmenter.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        mask = results.segmentation_mask
    if mask is None:
        return image
    mask_3 = cv2.cvtColor((mask > 0.5).astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
    blurred = cv2.GaussianBlur(image, (25, 25), 0)
    return np.where(mask_3 == 255, image, blurred)


def process_folder(
    input_dir: Path,
    output_dir: Path,
    enhance: bool,
    blur: bool,
    auto_enhance: bool,
    auto_blur: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in input_dir.iterdir():
        if path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            continue
        img = cv2.imread(str(path))
        if img is None:
            print(f"Skipping {path}")
            continue

        mask = None

        if enhance:
            img = enhance_color(img)
        elif auto_enhance:
            if is_washed_out(img):
                img = enhance_color(img)
            else:
                print(f"{path.name}: skipping enhance (not washed out)")

        if blur or auto_blur:
            if mask is None:
                with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as segmenter:
                    mask = segmenter.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).segmentation_mask

        if blur:
            img = blur_background(img, mask)
        elif auto_blur:
            if not background_is_blurred(img, mask):
                img = blur_background(img, mask)
            else:
                print(f"{path.name}: skipping blur (already blurred)")

        out_path = output_dir / path.name
        cv2.imwrite(str(out_path), img)
        print(f"Saved {out_path}")


def parse_args():
    p = argparse.ArgumentParser(description='Enhance portraits with optional background blur.')
    p.add_argument('input_dir', help='Folder of input images')
    p.add_argument('output_dir', help='Folder to save processed images')
    p.add_argument('--enhance', action='store_true', help='Improve color curves')
    p.add_argument('--blur', action='store_true', help='Blur background behind subject')
    p.add_argument('--auto-enhance', action='store_true', help='Enhance colors only if washed out')
    p.add_argument('--auto-blur', action='store_true', help='Blur background only if not already blurred')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if not (args.enhance or args.blur or args.auto_enhance or args.auto_blur):
        print('Nothing to do: specify --enhance/--auto-enhance or --blur/--auto-blur')
    process_folder(
        Path(args.input_dir),
        Path(args.output_dir),
        args.enhance,
        args.blur,
        args.auto_enhance,
        args.auto_blur,
    )
