# Portrait Fix

A simple script for enhancing portraits. It can perform two operations:

- **Color enhance**: improve color curves to avoid washed-out images using CLAHE.
- **Background blur**: blur everything behind the person using Mediapipe selfie segmentation.

You can run either or both operations with flags. There are also "auto" modes
that first check whether a fix is needed:

```
python process.py input_dir output_dir [--enhance] [--blur]
python process.py input_dir output_dir [--auto-enhance] [--auto-blur]
```

Install dependencies:

```
pip install -r requirements.txt
```
