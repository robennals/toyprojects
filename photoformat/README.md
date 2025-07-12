# Photo Format

This folder contains a small script that formats a directory full of photos into a consistent 2:3 portrait style.

## Usage

```bash
pip install -r requirements.txt
python format.py <input_folder> <output_folder>
```

The script will rotate images so that faces are upright, then crop them so that the detected face lies roughly in the top third of the result with a 2:3 aspect ratio (width:height).

