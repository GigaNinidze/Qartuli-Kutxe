"""Custom button components following design palette and consistent sizing."""

import customtkinter as ctk

# Color constants (Design Tokens)
PRIMARY_COLOR = "#FA8148"  # Crayola Orange (Primary action)
SUCCESS_COLOR = "#03CEA4"  # Mint (Confirmations)
NEUTRAL_BG = "#EDE7D1"     # Subtle neutral for secondary buttons
NEUTRAL_HOVER = "#D7CDB1"
NEUTRAL_TEXT = "#1F2937"    # Dark slate for text

DEFAULT_HEIGHT = 36
DEFAULT_CORNER = 12


class _BaseButton(ctk.CTkButton):
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=DEFAULT_HEIGHT,
            corner_radius=DEFAULT_CORNER,
            **kwargs,
        )


class PrimaryButton(_BaseButton):
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=PRIMARY_COLOR,
            hover_color="#E67330",
            text_color="#FFFFFF",
            **kwargs,
        )


class SuccessButton(_BaseButton):
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=SUCCESS_COLOR,
            hover_color="#02B08E",
            text_color="#FFFFFF",
            **kwargs,
        )


class SecondaryButton(_BaseButton):
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=NEUTRAL_BG,
            hover_color=NEUTRAL_HOVER,
            text_color=NEUTRAL_TEXT,
            **kwargs,
        )
