"""Main GUI window for the Georgian Advertisement Generator app."""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import List, Tuple

import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox

from config import api_keys, settings
from core import csv_handler, ad_generator
from prompts.tone_prompts import TONES
from utils.validation import row_is_complete

from .spreadsheet_ttk import SpreadsheetWidgetTTK
from .components.tone_selector import ToneSelector
from .components.buttons import PrimaryButton, SuccessButton


class MainApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title(settings.APP_NAME)
        self.geometry("1120x680")
        ctk.set_appearance_mode("light")
        # Global light palette
        self.configure(fg_color="#FFF5B2")  # Vanilla background

        # Root content container (ensures visible light background on macOS)
        content = ctk.CTkFrame(self, fg_color="#FFF5B2")
        content.pack(fill="both", expand=True)

        # ---- Top Controls ---- #
        top_frame = ctk.CTkFrame(content, fg_color="#FFF0A0", corner_radius=14)
        top_frame.pack(fill="x", padx=16, pady=16)

        # Tone dropdown with label
        tone_label = ctk.CTkLabel(top_frame, text="ტონი", text_color="#111827")
        tone_label.pack(side="left", padx=(12, 6), pady=10)
        self.tone_selector = ToneSelector(top_frame, width=160)
        self.tone_selector.pack(side="left", padx=(0, 16), pady=10)

        self.generate_btn = PrimaryButton(top_frame, text="Generate Ads", command=self._on_generate)
        self.generate_btn.pack(side="left", padx=8, pady=10)

        from .components.buttons import SecondaryButton, SuccessButton
        import_btn = SecondaryButton(top_frame, text="Import CSV", command=self._on_import)
        import_btn.pack(side="left", padx=8, pady=10)

        export_btn = SuccessButton(top_frame, text="Export CSV", command=self._on_export)
        export_btn.pack(side="left", padx=8, pady=10)

        api_btn = SecondaryButton(top_frame, text="Enter API Key", command=self._ask_api_key)
        api_btn.pack(side="left", padx=8, pady=10)

        # Progress label
        self.status_var = ctk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(top_frame, textvariable=self.status_var, text_color="#374151")
        status_label.pack(side="right", padx=12, pady=10)

        # ---- Spreadsheet ---- #
        self.sheet = SpreadsheetWidgetTTK(content)
        self.sheet.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # -------------------- Button Callbacks -------------------- #

    def _on_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            df = csv_handler.import_csv(file_path)
            self.sheet.load_dataframe(df)
            self.status_var.set(f"Loaded {Path(file_path).name}")
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Failed to load CSV: {exc}")

    def _on_export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            csv_handler.export_csv(self.sheet.as_dataframe(), file_path)
            self.status_var.set("Exported CSV successfully")
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Failed to export CSV: {exc}")

    def _ask_api_key(self):
        # Custom light-styled modal for API key entry
        modal = ctk.CTkToplevel(self)
        modal.title("API Key")
        modal.transient(self)
        modal.grab_set()
        modal.configure(fg_color="#FFFDF4")
        modal.geometry("520x180")

        wrapper = ctk.CTkFrame(modal, fg_color="#FFFDF4")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        label = ctk.CTkLabel(wrapper, text="Enter your OpenAI API key", text_color="#111827")
        label.pack(anchor="w")

        entry = ctk.CTkEntry(wrapper, placeholder_text="sk-...", width=480)
        entry.pack(fill="x", pady=12)

        def on_save():
            key = entry.get().strip()
            if not key:
                messagebox.showwarning("Empty", "Please paste your API key.")
                return
            if api_keys.validate_api_key(key):
                api_keys.save_api_key(key)
                messagebox.showinfo("Success", "API key saved!")
                modal.destroy()
            else:
                messagebox.showerror("Invalid", "Provided API key is invalid.")

        buttons = ctk.CTkFrame(wrapper, fg_color="#FFFDF4")
        buttons.pack(fill="x")
        from .components.buttons import PrimaryButton, SecondaryButton
        save_btn = PrimaryButton(buttons, text="Save", command=on_save)
        save_btn.pack(side="right")
        cancel_btn = SecondaryButton(buttons, text="Cancel", command=modal.destroy)
        cancel_btn.pack(side="right", padx=(0, 8))

    def _on_generate(self):
        if not api_keys.load_api_key():
            messagebox.showwarning("Missing API Key", "Please enter your OpenAI API key first.")
            return

        rows = self.sheet.iter_incomplete_rows()
        if not rows:
            messagebox.showinfo("Nothing to Generate", "No rows need ad generation.")
            return

        tone = self.tone_selector.current_tone()
        # Run generation in background thread to keep UI responsive
        threading.Thread(target=self._generate_ads_thread, args=(rows, tone), daemon=True).start()

    # -------------------- Generation Logic -------------------- #

    def _generate_ads_thread(self, rows: List[Tuple[str, str, str]], tone: str):
        self.status_var.set("Generating ads…")
        batch_size = 5
        idx = 0
        while idx < len(rows):
            batch = rows[idx : idx + batch_size]
            data_pairs = [(name, desc) for (_, name, desc) in batch]
            try:
                results = ad_generator.generate_batch(data_pairs, tone, concurrency=3)
            except Exception as exc:  # pylint: disable=broad-except
                messagebox.showerror("Generation Error", str(exc))
                break

            for (item_id, _, _), ad_text in zip(batch, results):
                if isinstance(ad_text, Exception):
                    ad_out = f"Error: {ad_text}"
                else:
                    ad_out = ad_text
                self.sheet.set_ad(item_id, ad_out)

            # Save progress after each batch
            temp_path = Path.home() / "tako_ads_autosave.csv"
            csv_handler.export_csv(self.sheet.as_dataframe(), temp_path)
            self.status_var.set(f"Processed {idx + len(batch)}/{len(rows)} rows…")
            idx += batch_size
            time.sleep(2)  # rate limiting gap between batches

        self.status_var.set("Generation complete ✔")
