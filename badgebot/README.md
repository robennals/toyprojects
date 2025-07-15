# Badge Crop

This script detects a white rectangular badge in a photo and crops the image to that badge. It is useful when people hold up name tags or cards that should be isolated.

## Usage

```bash
pip install -r requirements.txt
python crop.py input.jpg -o badge.jpg
```

If no badge is detected, the script prints a message and no file is written.
