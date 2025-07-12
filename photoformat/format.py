import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
import argparse

mp_face_detection = mp.solutions.face_detection
mp_pose = mp.solutions.pose

def rotate_image(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def align_face(image):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        for base_angle in [0, 90, -90, 180]:
            rotated = rotate_image(image, base_angle)
            results = face_detection.process(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))
            if results.detections:
                detection = results.detections[0]
                h, w = rotated.shape[:2]
                keypoints = detection.location_data.relative_keypoints
                right_eye = keypoints[0]
                left_eye = keypoints[1]
                eye_dx = (left_eye.x - right_eye.x) * w
                eye_dy = (left_eye.y - right_eye.y) * h
                roll = np.degrees(np.arctan2(eye_dy, eye_dx))
                total_angle = base_angle + roll
                return rotate_image(image, total_angle), total_angle
    return image, 0

def crop_portrait(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_pose.Pose(static_image_mode=True) as pose:
        result = pose.process(rgb)
    if not result.pose_landmarks:
        return None
    landmarks = result.pose_landmarks.landmark
    h, w = image.shape[:2]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    nose_x, nose_y = nose.x * w, nose.y * h
    hip_y = (left_hip.y + right_hip.y) / 2 * h
    H = int(1.5 * (hip_y - nose_y))
    if H <= 0:
        return None
    top = max(0, int(nose_y - H / 3))
    if top + H > h:
        H = h - top
    W = int(H * 2 / 3)
    center_x = int(nose_x)
    left = center_x - W // 2
    left = max(0, min(w - W, left))
    bottom = top + H
    right = left + W
    crop = image[top:bottom, left:right]
    return crop

def process_folder(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for img_path in input_dir.glob('*'):
        if not img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            continue
        image = cv2.imread(str(img_path))
        if image is None:
            continue
        rotated, _ = align_face(image)
        crop = crop_portrait(rotated)
        if crop is None:
            crop = rotated
        output_path = output_dir / img_path.name
        cv2.imwrite(str(output_path), crop)
        print(f"Processed {img_path} -> {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Format photos for portrait.')
    parser.add_argument('input_dir', help='Directory with input images')
    parser.add_argument('output_dir', help='Directory for processed images')
    args = parser.parse_args()
    process_folder(args.input_dir, args.output_dir)
