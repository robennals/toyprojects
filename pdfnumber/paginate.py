#!/usr/bin/env python3
"""Concatenate PDF files and add page numbers using HTML templates."""

import argparse
import io
import yaml
import pystache
from PyPDF2 import PdfReader, PdfWriter
from weasyprint import HTML


def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def render_number_page(template_str, number, width, height):
    renderer = pystache.Renderer()
    content = renderer.render(template_str, {'page_number': number})
    full_html = (
        f"<html><head><style>@page {{ size: {width}pt {height}pt; margin: 0; }}"
        "html, body { margin:0; padding:0; }" "</style></head><body>"
        f"{content}</body></html>"
    )
    pdf_bytes = HTML(string=full_html).write_pdf()
    return PdfReader(io.BytesIO(pdf_bytes)).pages[0]


def merge_pdfs(config):
    writer = PdfWriter()
    first = config.get('first_page', 1)
    last = config.get('last_page')

    global_index = 1
    number_index = 1

    for item in config['files']:
        reader = PdfReader(item['path'])
        template = item.get('template')
        left_template = item.get('left_template')
        right_template = item.get('right_template')
        pos = item.get('position', 'above')
        tmpl_cache = {}
        if template:
            tmpl_cache['single'] = load_template(template)
        if left_template:
            tmpl_cache['left'] = load_template(left_template)
        if right_template:
            tmpl_cache['right'] = load_template(right_template)

        for page in reader.pages:
            page_obj = page
            if global_index >= first and (last is None or global_index <= last):
                if left_template and right_template:
                    tmpl = tmpl_cache['right'] if number_index % 2 == 1 else tmpl_cache['left']
                elif template:
                    tmpl = tmpl_cache['single']
                elif left_template:
                    tmpl = tmpl_cache['left']
                elif right_template:
                    tmpl = tmpl_cache['right']
                else:
                    tmpl = None
                if tmpl:
                    overlay = render_number_page(
                        tmpl,
                        number_index,
                        page_obj.mediabox.width,
                        page_obj.mediabox.height,
                    )
                    if pos == 'above':
                        page_obj.merge_page(overlay)
                    else:  # below
                        overlay.merge_page(page_obj)
                        page_obj = overlay
                    number_index += 1
            writer.add_page(page_obj)
            global_index += 1

    output = config.get('output', 'output.pdf')
    with open(output, 'wb') as f:
        writer.write(f)
    print(f"Wrote {output}")


def main():
    parser = argparse.ArgumentParser(description='Merge PDFs with page numbers.')
    parser.add_argument('config', help='YAML configuration file')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    merge_pdfs(config)


if __name__ == '__main__':
    main()
