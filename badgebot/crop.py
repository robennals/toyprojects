#!/usr/bin/env python3
"""Crop a white rectangular badge from an image if present."""

import argparse
from pathlib import Path
import cv2
import numpy as np


def find_badge(image: np.ndarray):
    """Return bounding box (x, y, w, h) of the most likely badge or None."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # threshold for bright regions
    _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_area = image.shape[0] * image.shape[1]
    best_rect = None
    best_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < img_area * 0.01:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if area > best_area:
                best_area = area
                best_rect = (x, y, w, h)
    return best_rect


def crop_badge(image: np.ndarray):
    rect = find_badge(image)
    if rect is None:
        return None
    x, y, w, h = rect
    return image[y : y + h, x : x + w]


def main():
    parser = argparse.ArgumentParser(description="Crop white badge from an image if found")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("-o", "--output", default="badge.jpeg", help="Output file path")
    args = parser.parse_args()

    img = cv2.imread(args.image)
    if img is None:
        parser.error(f"Could not read {args.image}")

    badge = crop_badge(img)
    if badge is None:
        print("No badge detected")
        return
    cv2.imwrite(args.output, badge)
    print(f"Saved badge crop to {args.output}")


if __name__ == "__main__":
    main()
