#!/usr/bin/env python3
"""Crop a white rectangular badge from an image if present."""

import argparse
import cv2
import numpy as np


def find_badge(image: np.ndarray):
    """Return bounding box (x, y, w, h) of the most likely badge or ``None``."""

    # Resize large images for faster processing while keeping a scale factor
    scale = 1000.0 / image.shape[1]
    if scale < 1.0:
        small = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        factor = 1.0 / scale
    else:
        small = image
        factor = 1.0

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Automatically choose a threshold value with Otsu's method
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_area = small.shape[0] * small.shape[1]

    best_rect = None
    best_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < img_area * 0.005:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect = w / float(h)
            if 0.5 <= aspect <= 2.0 and area > best_area:
                best_area = area
                best_rect = (int(x * factor), int(y * factor), int(w * factor), int(h * factor))

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
