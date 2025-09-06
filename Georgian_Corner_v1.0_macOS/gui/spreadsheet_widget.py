"""Spreadsheet-like widget using ttk Treeview inside CustomTkinter Frame."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, List, Tuple

import pandas as pd
import customtkinter as ctk
from tkinter import ttk

from utils.validation import row_is_complete

COLUMNS = ("name", "description", "ad")


class SpreadsheetWidget(ctk.CTkFrame):
    """A minimal editable spreadsheet widget with three columns."""

    def __init__(self, master, rows: int = 50, **kwargs):
        super().__init__(master, **kwargs)

        style = ttk.Style()
        try:
            style.theme_use("default")
        except Exception:
            pass
        # Apple-like subtle table: light background, slight borders, rounded rows feel
        style.configure(
            "Treeview",
            background="#FFFDF4",
            fieldbackground="#FFFDF4",
            foreground="#1F2937",
            rowheight=28,
            bordercolor="#E5E7EB",
            borderwidth=1,
            relief="groove",
        )
        style.configure("Treeview.Heading", background="#F7F3E3", foreground="#111827")
        style.map("Treeview",
                   background=[("selected", "#E8F5F2")],
                   foreground=[("selected", "#0B3D2E")])

        container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=14)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(master=container, columns=COLUMNS, show="headings", height=rows)
        for col, heading in zip(COLUMNS, ("პროდუქტის სახელი", "აღწერა", "რეკლამა")):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=220 if col != "ad" else 360, stretch=True)

        self.tree.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=1)

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Double-click to edit cell
        self.tree.bind("<Double-1>", self._on_double_click)

        # Prepopulate empty rows
        for _ in range(rows):
            self.tree.insert("", "end", values=("", "", ""))

    # -------------------- Data Helpers -------------------- #

    def as_dataframe(self) -> pd.DataFrame:
        data = [self.tree.item(i, "values") for i in self.tree.get_children()]
        return pd.DataFrame(data, columns=COLUMNS)

    def load_dataframe(self, df: pd.DataFrame):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert rows
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(row["name"], row["description"], row.get("ad", "")))

    def iter_incomplete_rows(self) -> List[Tuple[str, str, str]]:
        """Return (item_id, name, description) for rows missing an ad but having inputs."""
        result = []
        for idx, item in enumerate(self.tree.get_children()):
            name, desc, ad = self.tree.item(item, "values")
            if row_is_complete(name, desc) and not ad.strip():
                result.append((item, name, desc))
        return result

    def set_ad(self, item_id: str, ad_text: str):
        name, desc, _ = self.tree.item(item_id, "values")
        self.tree.item(item_id, values=(name, desc, ad_text))

    # -------------------- Cell Editing -------------------- #

    def _on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        x, y, width, height = self.tree.bbox(row_id, column)
        value = self.tree.set(row_id, column)

        entry = ctk.CTkEntry(self.tree, width=width)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def _save_edit(event):
            self.tree.set(row_id, column, entry.get())
            entry.destroy()

        entry.bind("<Return>", _save_edit)
        entry.bind("<Escape>", lambda _e: entry.destroy())
