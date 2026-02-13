"""GPS accuracy indicator widget.

Shows accuracy in meters with a color-coded badge:
  green = good (<10m), yellow = ok (10-25m), red = poor (>25m)
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.properties import NumericProperty

from presentation.theme import Colors, Sizing


class AccuracyIndicator(BoxLayout):
    accuracy = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.size = (130, 36)
        self.padding = [10, 4]
        self.spacing = 6

        with self.canvas.before:
            Color(*Colors.OVERLAY_BG)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[Sizing.BORDER_RADIUS]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

        # status dot
        self._dot_color = Color(*Colors.ACCENT_SUCCESS)
        self._dot = None

        self._label = Label(
            text="±0m",
            font_size=Sizing.FONT_SMALL,
            color=Colors.TEXT_PRIMARY,
        )
        self.add_widget(self._label)

        self.bind(accuracy=self._on_accuracy)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_accuracy(self, *args):
        acc = self.accuracy
        self._label.text = f"GPS ±{acc:.0f}m"

        if acc < 10:
            self._label.color = Colors.ACCENT_SUCCESS
        elif acc < 25:
            self._label.color = Colors.ACCENT_WARN
        else:
            self._label.color = Colors.ACCENT_ERROR
