"""Pure ttk main window for maximal compatibility and clear, light design."""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import List, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config import api_keys, settings
from core import csv_handler, ad_generator
from prompts.tone_prompts import TONES

from .spreadsheet_ttk import SpreadsheetWidgetTTK


class MainApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(settings.APP_NAME)
        self.geometry("1120x720")

        # Enforce a light theme and minimal aesthetic
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.configure(background="#FFF5B2")  # Vanilla background

        # Top container
        top = ttk.Frame(self, padding=(16, 16))
        top.pack(fill="x")

        # Tone selector
        tone_label = ttk.Label(top, text="ტონი", foreground="#111827", background="#FFF5B2")
        tone_label.pack(side="left", padx=(0, 8))
        self.tone_var = tk.StringVar(value=list(TONES.keys())[0])
        tone = ttk.Combobox(top, textvariable=self.tone_var, values=list(TONES.keys()), state="readonly")
        tone.pack(side="left")

        # Button styles
        style.configure("Primary.TButton", foreground="#FFFFFF", background="#FA8148")
        style.map("Primary.TButton", background=[("active", "#E67330")])
        style.configure("Success.TButton", foreground="#FFFFFF", background="#03CEA4")
        style.map("Success.TButton", background=[("active", "#02B08E")])
        style.configure("Secondary.TButton", foreground="#1F2937", background="#EDE7D1")
        style.map("Secondary.TButton", background=[("active", "#D7CDB1")])

        gen_btn = ttk.Button(top, text="Generate Ads", style="Primary.TButton", command=self._on_generate)
        gen_btn.pack(side="left", padx=8)

        import_btn = ttk.Button(top, text="Import CSV", style="Secondary.TButton", command=self._on_import)
        import_btn.pack(side="left", padx=8)

        export_btn = ttk.Button(top, text="Export CSV", style="Success.TButton", command=self._on_export)
        export_btn.pack(side="left", padx=8)

        api_btn = ttk.Button(top, text="Enter API Key", style="Secondary.TButton", command=self._ask_api_key)
        api_btn.pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(top, textvariable=self.status_var, background="#FFF5B2", foreground="#374151")
        status.pack(side="right")

        # Spreadsheet
        sheet_container = ttk.Frame(self, padding=(16, 0, 16, 16))
        sheet_container.pack(fill="both", expand=True)
        self.sheet = SpreadsheetWidgetTTK(sheet_container)
        self.sheet.pack(fill="both", expand=True)

    # -------------------- Callbacks -------------------- #
    def _on_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            df = csv_handler.import_csv(file_path)
            self.sheet.load_dataframe(df)
            self.status_var.set(f"Loaded {Path(file_path).name}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Failed to load CSV: {exc}")

    def _on_export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            csv_handler.export_csv(self.sheet.as_dataframe(), file_path)
            self.status_var.set("Exported CSV successfully")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Failed to export CSV: {exc}")

    def _ask_api_key(self):
        win = tk.Toplevel(self)
        win.title("API Key")
        win.configure(background="#FFFDF4")
        win.transient(self)
        win.grab_set()
        frm = ttk.Frame(win, padding=16)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Enter your OpenAI API key", background="#FFFDF4").pack(anchor="w")
        entry = ttk.Entry(frm)
        entry.pack(fill="x", pady=8)

        def on_save():
            key = entry.get().strip()
            if not key:
                messagebox.showwarning("Empty", "Please paste your API key.")
                return
            if api_keys.validate_api_key(key):
                api_keys.save_api_key(key)
                messagebox.showinfo("Success", "API key saved!")
                win.destroy()
            else:
                messagebox.showerror("Invalid", "Provided API key is invalid.")

        buttons = ttk.Frame(frm)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=on_save).pack(side="right")
        ttk.Button(buttons, text="Cancel", style="Secondary.TButton", command=win.destroy).pack(side="right", padx=(0, 8))

    def _on_generate(self):
        if not api_keys.load_api_key():
            messagebox.showwarning("Missing API Key", "Please enter your OpenAI API key first.")
            return
        rows = self.sheet.iter_incomplete_rows()
        if not rows:
            messagebox.showinfo("Nothing to Generate", "No rows need ad generation.")
            return
        tone = self.tone_var.get()
        threading.Thread(target=self._generate_ads_thread, args=(rows, tone), daemon=True).start()

    def _generate_ads_thread(self, rows: List[Tuple[str, str, str]], tone: str):
        self.status_var.set("Generating ads…")
        batch_size = 5
        idx = 0
        while idx < len(rows):
            batch = rows[idx : idx + batch_size]
            data_pairs = [(name, desc) for (_, name, desc) in batch]
            try:
                results = ad_generator.generate_batch(data_pairs, tone, concurrency=3)
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Generation Error", str(exc))
                break
            for (item_id, _, _), ad_text in zip(batch, results):
                self.sheet.set_ad(item_id, ad_text if not isinstance(ad_text, Exception) else f"Error: {ad_text}")
            temp_path = Path.home() / "tako_ads_autosave.csv"
            csv_handler.export_csv(self.sheet.as_dataframe(), temp_path)
            self.status_var.set(f"Processed {idx + len(batch)}/{len(rows)} rows…")
            idx += batch_size
            time.sleep(2)

