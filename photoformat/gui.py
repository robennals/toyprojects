import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import traceback
from pathlib import Path

from format import process_folder


def run_processing(input_dir, output_dir, log_widget):
    try:
        process_folder(input_dir, output_dir)
        log_widget.insert(tk.END, "Processing complete\n")
    except Exception as e:
        log_widget.insert(tk.END, f"Error: {e}\n")
        log_widget.insert(tk.END, traceback.format_exc())
        messagebox.showerror("Error", str(e))


def start_processing(input_var, output_var, log_widget, start_button):
    input_dir = input_var.get()
    output_dir = output_var.get()
    if not input_dir or not output_dir:
        messagebox.showwarning("Missing folders", "Please select both input and output folders.")
        return
    start_button.config(state=tk.DISABLED)
    log_widget.delete(1.0, tk.END)
    thread = threading.Thread(target=lambda: [run_processing(input_dir, output_dir, log_widget), start_button.config(state=tk.NORMAL)])
    thread.start()


def browse_directory(variable):
    directory = filedialog.askdirectory()
    if directory:
        variable.set(directory)


def main():
    root = tk.Tk()
    root.title("Photo Format")

    input_var = tk.StringVar()
    output_var = tk.StringVar()

    tk.Label(root, text="Input Folder:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=input_var, width=40).grid(row=0, column=1, padx=5)
    tk.Button(root, text="Browse", command=lambda: browse_directory(input_var)).grid(row=0, column=2, padx=5)

    tk.Label(root, text="Output Folder:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=output_var, width=40).grid(row=1, column=1, padx=5)
    tk.Button(root, text="Browse", command=lambda: browse_directory(output_var)).grid(row=1, column=2, padx=5)

    log_widget = scrolledtext.ScrolledText(root, width=60, height=15)
    log_widget.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    start_button = tk.Button(root, text="Run", command=lambda: start_processing(input_var, output_var, log_widget, start_button))
    start_button.grid(row=3, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
