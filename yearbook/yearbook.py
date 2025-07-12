#!/usr/bin/env python3
import argparse
import os
import pandas as pd
from weasyprint import HTML
import pystache

HTML_TEMPLATE_DEFAULT = """
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
.page {
  page-break-after: always;
  width: 8.5in;
  height: 11in;
  padding: 1in;
  box-sizing: border-box;
}
.page:last-child { page-break-after: auto; }
</style>
</head>
<body>
{{#pages}}
<div class="page">
{{{html}}}
</div>
{{/pages}}
</body>
</html>
"""


def render_pages(dataframe, template_str, photo_base):
    renderer = pystache.Renderer()
    pages = []
    for _, row in dataframe.iterrows():
        context = row.to_dict()
        if photo_base:
            path = os.path.join(photo_base, str(row.get('photo', '')))
            context['photo'] = os.path.abspath(path)
        html = renderer.render(template_str, context)
        pages.append({'html': html})
    return pages


def generate_pdf(pages, output_path):
    renderer = pystache.Renderer()
    full_html = renderer.render(HTML_TEMPLATE_DEFAULT, {'pages': pages})
    HTML(string=full_html, base_url='.').write_pdf(output_path)


def main():
    parser = argparse.ArgumentParser(description='Generate yearbook PDF from spreadsheet and template.')
    parser.add_argument('spreadsheet', help='CSV file with columns name, quote, home town, birthday, photo')
    parser.add_argument('template', help='Mustache HTML template for a single page')
    parser.add_argument('-o', '--output', default='yearbook.pdf', help='Output PDF file path')
    parser.add_argument('--photo-base', default='', help='Base path or URL prefix for photos')
    args = parser.parse_args()

    df = pd.read_csv(args.spreadsheet)
    with open(args.template, 'r', encoding='utf-8') as f:
        template_str = f.read()
    pages = render_pages(df, template_str, args.photo_base)
    generate_pdf(pages, args.output)
    print(f'Generated {args.output} with {len(pages)} pages.')


if __name__ == '__main__':
    main()
