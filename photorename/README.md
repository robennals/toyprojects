# Photo Rename

This folder contains a simple script `rename.py` that renames photos based on badge images.

## Usage

```bash
pip install -r requirements.txt
sudo apt-get install -y tesseract-ocr
python rename.py names.csv /path/to/input_photos /path/to/output_photos
```

The script expects `names.csv` to contain a column called `name`.  It looks for
badge photos where the badge text matches one of these names.  When a badge is
found the following five photos are scanned for additional pictures of the same
person without the badge using a simple face comparison based on OpenCV.  The matched images are copied
to the output directory and renamed as described in the script.

Unmatched images are copied to the `unmatched` folder inside the output
location.

The script relies on the `tesseract` command line tool for OCR. Install
`tesseract-ocr` from your system package manager if it is not already available.
