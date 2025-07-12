import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import traceback

from yearbook import generate_pdf, render_pages
import pandas as pd


def run_processing(spreadsheet, template, output_path, photo_base, per_page,
                   log_widget):
    try:
        df = pd.read_csv(spreadsheet)
        with open(template, 'r', encoding='utf-8') as f:
            template_str = f.read()
        pages = render_pages(df, template_str, photo_base, per_page)
        generate_pdf(pages, output_path)
        log_widget.insert(tk.END, f"Generated {output_path}\n")
    except Exception as e:
        log_widget.insert(tk.END, f"Error: {e}\n")
        log_widget.insert(tk.END, traceback.format_exc())
        messagebox.showerror("Error", str(e))


def start_processing(spreadsheet_var, template_var, output_var, photo_base_var,
                      per_page_var, log_widget, start_button):
    spreadsheet = spreadsheet_var.get()
    template = template_var.get()
    output_path = output_var.get() or 'yearbook.pdf'
    photo_base = photo_base_var.get()
    per_page = per_page_var.get() or 1
    if not spreadsheet or not template:
        messagebox.showwarning(
            "Missing fields", "Please select spreadsheet and template files.")
        return
    start_button.config(state=tk.DISABLED)
    log_widget.delete(1.0, tk.END)
    thread = threading.Thread(target=lambda: [
        run_processing(spreadsheet, template, output_path, photo_base,
                       per_page, log_widget),
        start_button.config(state=tk.NORMAL)
    ])
    thread.start()


def browse_file(variable):
    path = filedialog.askopenfilename()
    if path:
        variable.set(path)


def browse_save_file(variable):
    path = filedialog.asksaveasfilename(defaultextension='.pdf',
                                        filetypes=[('PDF files', '*.pdf')])
    if path:
        variable.set(path)


def browse_directory(variable):
    directory = filedialog.askdirectory()
    if directory:
        variable.set(directory)


def main():
    root = tk.Tk()
    root.title("Yearbook")

    spreadsheet_var = tk.StringVar()
    template_var = tk.StringVar()
    output_var = tk.StringVar(value='yearbook.pdf')
    photo_base_var = tk.StringVar()
    per_page_var = tk.IntVar(value=1)

    tk.Label(root, text="Spreadsheet:").grid(row=0, column=0, sticky="e", padx=5,
                                               pady=5)
    tk.Entry(root, textvariable=spreadsheet_var, width=40).grid(row=0, column=1,
                                                                padx=5)
    tk.Button(root, text="Browse",
              command=lambda: browse_file(spreadsheet_var)).grid(row=0, column=2,
                                                                padx=5)

    tk.Label(root, text="Template:").grid(row=1, column=0, sticky="e", padx=5,
                                           pady=5)
    tk.Entry(root, textvariable=template_var, width=40).grid(row=1, column=1,
                                                             padx=5)
    tk.Button(root, text="Browse",
              command=lambda: browse_file(template_var)).grid(row=1, column=2,
                                                              padx=5)

    tk.Label(root, text="Output PDF:").grid(row=2, column=0, sticky="e", padx=5,
                                             pady=5)
    tk.Entry(root, textvariable=output_var, width=40).grid(row=2, column=1,
                                                           padx=5)
    tk.Button(root, text="Browse",
              command=lambda: browse_save_file(output_var)).grid(row=2, column=2,
                                                                 padx=5)

    tk.Label(root, text="Photo Base:").grid(row=3, column=0, sticky="e", padx=5,
                                             pady=5)
    tk.Entry(root, textvariable=photo_base_var, width=40).grid(row=3, column=1,
                                                               padx=5)
    tk.Button(root, text="Browse",
              command=lambda: browse_directory(photo_base_var)).grid(row=3,
                                                                    column=2,
                                                                    padx=5)

    tk.Label(root, text="Profiles per Page:").grid(row=4, column=0, sticky="e",
                                                    padx=5, pady=5)
    tk.Entry(root, textvariable=per_page_var, width=40).grid(row=4, column=1,
                                                             padx=5)

    log_widget = scrolledtext.ScrolledText(root, width=60, height=15)
    log_widget.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    start_button = tk.Button(
        root,
        text="Run",
        command=lambda: start_processing(spreadsheet_var, template_var, output_var,
                                         photo_base_var, per_page_var, log_widget,
                                         start_button)
    )
    start_button.grid(row=6, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
