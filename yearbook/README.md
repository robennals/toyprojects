# Yearbook

This folder contains a small script to generate a PDF yearbook from a CSV file and an HTML Mustache template.

## Usage

```bash
pip install -r requirements.txt
python yearbook.py data.csv template.html -o output.pdf

# Render two people per page
python yearbook.py data.csv template_2.html --per-page 2 -o output2.pdf
```

A basic cross‑platform GUI is also available. It now includes a field to set how
many profiles appear on each page:

```bash
python gui.py
```
