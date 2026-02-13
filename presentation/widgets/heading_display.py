"""Heading display widget shown at top of camera screen.

Shows compass bearing and cardinal direction with a little compass indicator.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

from presentation.theme import Colors, Sizing


class HeadingDisplay(BoxLayout):
    heading = NumericProperty(0.0)
    cardinal = StringProperty("N")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.size = (180, 50)
        self.pos_hint = {"center_x": 0.5}
        self.padding = [12, 6]
        self.spacing = 8

        # background
        with self.canvas.before:
            Color(*Colors.OVERLAY_BG)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[Sizing.BORDER_RADIUS]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._heading_label = Label(
            text="0°",
            font_size=Sizing.FONT_TITLE,
            color=Colors.TEXT_PRIMARY,
            bold=True,
            halign="right",
            size_hint_x=0.6,
        )
        self._cardinal_label = Label(
            text="N",
            font_size=Sizing.FONT_BODY,
            color=Colors.ACCENT,
            halign="left",
            size_hint_x=0.4,
        )

        self.add_widget(self._heading_label)
        self.add_widget(self._cardinal_label)

        self.bind(heading=self._on_update)
        self.bind(cardinal=self._on_update)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_update(self, *args):
        self._heading_label.text = f"{self.heading:.0f}°"
        self._cardinal_label.text = self.cardinal
