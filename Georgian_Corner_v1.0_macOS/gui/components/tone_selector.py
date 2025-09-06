"""Dropdown component for tone selection."""
from __future__ import annotations

import customtkinter as ctk

from prompts.tone_prompts import TONES


class ToneSelector(ctk.CTkOptionMenu):
    def __init__(self, master, **kwargs):
        # Explicit light colors to avoid blending into dark bg
        super().__init__(
            master,
            values=list(TONES.keys()),
            fg_color="#FFFFFF",
            button_color="#FA8148",
            button_hover_color="#E67330",
            text_color="#111827",
            **kwargs,
        )
        self.set(list(TONES.keys())[0])

    def current_tone(self) -> str:
        return self.get()
