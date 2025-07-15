# PDF Page Number Merger

This tool concatenates multiple PDF files and applies page numbers using
Mustache HTML templates.  The templates are rendered with `{{page_number}}`
and converted to PDF using WeasyPrint.

## Configuration

Create a YAML file describing the input files and numbering options:

```yaml
output: combined.pdf           # optional, defaults to output.pdf
first_page: 1                  # first page to number (1-indexed)
last_page: null                # last page to number, omit for all pages
files:
  - path: intro.pdf
    template: numbers.html     # or left_template/right_template
    position: above            # "above" or "below" the existing content
  - path: chapters.pdf
    left_template: left.html
    right_template: right.html
    position: below
```

`template` is used for all pages if provided.  Alternatively specify both
`left_template` and `right_template` for alternating layouts.  Page numbers
start at 1 on `first_page` and increase only on numbered pages.

## Usage

Install dependencies and run the script with the YAML file:

```bash
pip install -r requirements.txt
python paginate.py config.yml
```

The merged PDF will be written to the `output` path.
