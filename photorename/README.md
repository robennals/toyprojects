# Photo Rename

This folder contains a simple script `rename.py` that renames photos based on badge images.

## Usage

```bash
pip install -r requirements.txt
sudo apt-get install -y tesseract-ocr
python rename.py names.csv /path/to/input_photos /path/to/output_photos
```

Optional arguments:

```
--first_last      spreadsheet uses first and last name columns instead of a single name column
--skip_rows N     skip the first N rows in the spreadsheet
--badge_dir DIR   save cropped badge images to this folder
```

A small cross‑platform GUI is also available:

```bash
python gui.py
```

The script expects `names.csv` to contain a column called `name` by default.
With the `--first_last` option, the first two columns are treated as first and
last names instead.  Use `--skip_rows N` to ignore header lines or other data at
the top of the sheet.  The script looks for badge photos where the badge text
matches one of these names.  When a badge is
found the following five photos are scanned for additional pictures of the same
person without the badge using a simple face comparison based on OpenCV.  Before
OCR the badge area is automatically cropped.  Cropped badges can optionally be
saved with ``--badge_dir`` for inspection.  The matched images are copied
to the output directory and renamed as described in the script.

Unmatched images are copied to the `unmatched` folder inside the output
location.

The script relies on the `tesseract` command line tool for OCR. Install
`tesseract-ocr` from your system package manager if it is not already available.
