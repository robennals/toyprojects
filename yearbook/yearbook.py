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
@page {
  size: 8.5in 11in;
  margin: 0;
}
.page {
  page-break-after: always;
  width: 8.5in;
  height: 11in;
  margin: 0;
  padding: 0;
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


def render_pages(dataframe, template_str, photo_base, per_page=1):
    """Render a list of HTML pages from the dataframe.

    ``per_page`` specifies how many profiles should be rendered on a single
    page of the output. Template variables are suffixed with the position
    number starting at 1 (e.g. ``name1``, ``name2``) to reference the correct
    profile.
    """

    renderer = pystache.Renderer()
    pages = []

    batch = []
    for _, row in dataframe.iterrows():
        batch.append(row)
        if len(batch) == per_page:
            context = {}
            for idx, r in enumerate(batch, start=1):
                for key, value in r.to_dict().items():
                    if photo_base and key == 'photo':
                        path = os.path.join(photo_base, str(value))
                        value = os.path.abspath(path)
                    context[f"{key}{idx}"] = value
            html = renderer.render(template_str, context)
            pages.append({'html': html})
            batch = []

    if batch:
        context = {}
        for idx, r in enumerate(batch, start=1):
            for key, value in r.to_dict().items():
                if photo_base and key == 'photo':
                    path = os.path.join(photo_base, str(value))
                    value = os.path.abspath(path)
                context[f"{key}{idx}"] = value
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
    parser.add_argument('-o', '--output', default='yearbook.pdf',
                        help='Output PDF file path')
    parser.add_argument('--photo-base', default='',
                        help='Base path or URL prefix for photos')
    parser.add_argument('--per-page', type=int, default=1,
                        help='Number of profiles to render per page')
    args = parser.parse_args()

    df = pd.read_csv(args.spreadsheet)
    with open(args.template, 'r', encoding='utf-8') as f:
        template_str = f.read()
    pages = render_pages(df, template_str, args.photo_base, args.per_page)
    generate_pdf(pages, args.output)
    print(f'Generated {args.output} with {len(pages)} pages.')


if __name__ == '__main__':
    main()
