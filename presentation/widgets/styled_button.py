"""Custom styled buttons that match our Material 3 look."""
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty

from presentation.theme import Colors, Sizing


class PrimaryButton(Button):
    """Filled accent-colored button."""

    bg_color = ListProperty(Colors.BUTTON_BG)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", Sizing.BUTTON_HEIGHT)
        kwargs.setdefault("font_size", Sizing.FONT_BODY)
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)  # transparent default bg
        self.color = Colors.BUTTON_TEXT

        with self.canvas.before:
            self._bg_color = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[Sizing.BORDER_RADIUS]
            )
        self.bind(pos=self._update, size=self._update, bg_color=self._update_color)

    def _update(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_color(self, *args):
        self._bg_color.rgba = self.bg_color

    def on_press(self):
        self._bg_color.rgba = Colors.ACCENT_DARK
        return super().on_press()

    def on_release(self):
        self._bg_color.rgba = self.bg_color
        return super().on_release()


class SecondaryButton(Button):
    """Outlined / ghost style button."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", Sizing.BUTTON_HEIGHT)
        kwargs.setdefault("font_size", Sizing.FONT_BODY)
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = Colors.ACCENT

        with self.canvas.before:
            Color(*Colors.BG_SURFACE[:3], 0.5)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[Sizing.BORDER_RADIUS]
            )
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
