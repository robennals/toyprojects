# toyprojects

A repo I use for various experimental toy projects. Anything interesting will get moved somewhere else.

## Yearbook Workflow

This repository contains several small tools that can be combined to produce a simple yearbook.

1. **Create a spreadsheet**
   
   Start with a CSV file containing at least a `name` column. You may add extra columns for quotes or other personal information.

2. **Take badge photos**
   
   Photograph each person holding their badge followed by one or more photos without the badge. Keep all images together in a single folder.

3. **Run the naming script**
   
   Use `photorename/rename.py` to scan the badge photos and rename the pictures according to the matching name in the spreadsheet.
   ```bash
   pip install -r photorename/requirements.txt
   sudo apt-get install -y tesseract-ocr
   python photorename/rename.py names.csv /path/to/raw_photos renamed_photos
   ```
   Matched images will be copied to the output directory with names like `Alice-1.jpeg` and `Alice-badge.jpeg`.

4. **Format the photos**
   
   Process the renamed images with `photoformat/format.py` to crop and rotate them into a consistent portrait layout.
   ```bash
   pip install -r photoformat/requirements.txt
   python photoformat/format.py renamed_photos formatted_photos
   ```

5. **Link photos in the spreadsheet**
   
   A script still needs to be written to update the CSV so that each person points to their formatted photo file. The intended workflow is to read the filenames produced above and add a `photo` column to the spreadsheet.

6. **Edit the template**
   
   Adjust `yearbook/examples/template.html` (or create your own Mustache template) to control how each page looks.

7. **Generate the yearbook pages**
   
   Use `yearbook/yearbook.py` to create a PDF for all people in the spreadsheet.
   ```bash
   pip install -r yearbook/requirements.txt
   python yearbook/yearbook.py data.csv template.html -o yearbook.pdf --photo-base formatted_photos
   ```

8. **Merge with other sections**
   
   Finally, use any PDF merge tool to combine the generated pages with other material such as introductions or advertisements.

