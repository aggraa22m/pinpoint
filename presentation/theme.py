"""App theme constants.

Centralized colors, fonts, sizing so we're not scattering magic numbers
all over the place. Supports dark and light mode.
"""
from kivy.utils import get_color_from_hex


class AppColors:
    """Dark theme colors (default). Material 3 inspired palette."""

    # backgrounds
    BG_PRIMARY = get_color_from_hex("#0F1117")
    BG_SURFACE = get_color_from_hex("#1A1D27")
    BG_CARD = get_color_from_hex("#222633")

    # accent
    ACCENT = get_color_from_hex("#4FC3F7")      # light blue
    ACCENT_DARK = get_color_from_hex("#0288D1")
    ACCENT_SUCCESS = get_color_from_hex("#66BB6A")
    ACCENT_WARN = get_color_from_hex("#FFA726")
    ACCENT_ERROR = get_color_from_hex("#EF5350")

    # text
    TEXT_PRIMARY = get_color_from_hex("#E8EAED")
    TEXT_SECONDARY = get_color_from_hex("#9AA0A6")
    TEXT_HINT = get_color_from_hex("#5F6368")

    # UI elements
    BUTTON_BG = get_color_from_hex("#4FC3F7")
    BUTTON_TEXT = get_color_from_hex("#0F1117")
    INPUT_BG = get_color_from_hex("#2A2E3A")
    DIVIDER = get_color_from_hex("#2E3240")

    # overlay (for camera screen)
    OVERLAY_BG = (0, 0, 0, 0.55)


class AppColorsLight:
    """Light theme — not used by default but here if needed."""

    BG_PRIMARY = get_color_from_hex("#FAFAFA")
    BG_SURFACE = get_color_from_hex("#FFFFFF")
    BG_CARD = get_color_from_hex("#F5F5F5")

    ACCENT = get_color_from_hex("#0288D1")
    ACCENT_DARK = get_color_from_hex("#01579B")
    ACCENT_SUCCESS = get_color_from_hex("#43A047")
    ACCENT_WARN = get_color_from_hex("#FB8C00")
    ACCENT_ERROR = get_color_from_hex("#E53935")

    TEXT_PRIMARY = get_color_from_hex("#202124")
    TEXT_SECONDARY = get_color_from_hex("#5F6368")
    TEXT_HINT = get_color_from_hex("#9AA0A6")

    BUTTON_BG = get_color_from_hex("#0288D1")
    BUTTON_TEXT = get_color_from_hex("#FFFFFF")
    INPUT_BG = get_color_from_hex("#EEEEEE")
    DIVIDER = get_color_from_hex("#E0E0E0")

    OVERLAY_BG = (1, 1, 1, 0.55)


# active theme — swap this to AppColorsLight for light mode
Colors = AppColors


class Sizing:
    PADDING = 16
    PADDING_SM = 8
    PADDING_LG = 24
    BORDER_RADIUS = 12
    BUTTON_HEIGHT = 48
    ICON_SIZE = 24
    FONT_TITLE = 22
    FONT_BODY = 16
    FONT_SMALL = 13
    FONT_HEADING = 32
