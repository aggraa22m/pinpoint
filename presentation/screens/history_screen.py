"""History screen — list of previously saved locations.

Shows saved results in a scrollable list. Each entry can be tapped
to open in maps, or swiped/deleted.
"""
import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.logger import Logger

from presentation.theme import Colors, Sizing
from presentation.widgets.styled_button import PrimaryButton, SecondaryButton


class HistoryScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="history", **kwargs)
        self.app = app_ref
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(
            orientation="vertical",
            padding=Sizing.PADDING,
            spacing=Sizing.PADDING_SM,
        )

        with root.canvas.before:
            Color(*Colors.BG_PRIMARY)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda *a: setattr(self._bg, "pos", root.pos),
            size=lambda *a: setattr(self._bg, "size", root.size),
        )

        # header row
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
        )
        header.add_widget(Label(
            text="Saved Locations",
            font_size=Sizing.FONT_HEADING,
            color=Colors.TEXT_PRIMARY,
            bold=True,
            halign="left",
        ))
        root.add_widget(header)

        # scrollable list area
        scroll = ScrollView(size_hint=(1, 1))
        self._list_layout = GridLayout(
            cols=1,
            spacing=Sizing.PADDING_SM,
            size_hint_y=None,
            padding=[0, Sizing.PADDING_SM],
        )
        self._list_layout.bind(
            minimum_height=self._list_layout.setter("height")
        )
        scroll.add_widget(self._list_layout)
        root.add_widget(scroll)

        # empty state label (hidden when there are items)
        self._empty_label = Label(
            text="No saved locations yet.\nLocate an object to get started.",
            font_size=Sizing.FONT_BODY,
            color=Colors.TEXT_HINT,
            halign="center",
            size_hint_y=None,
            height=100,
        )

        # bottom back button
        back_btn = SecondaryButton(text="BACK", size_hint_y=None, height=48)
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "camera"))
        root.add_widget(back_btn)

        self.add_widget(root)

    def on_enter(self):
        """Refresh list every time screen is shown."""
        self._refresh_list()

    def _refresh_list(self):
        self._list_layout.clear_widgets()

        locations = self.app.repo.get_all()

        if not locations:
            self._list_layout.add_widget(self._empty_label)
            return

        for idx, loc in enumerate(locations):
            card = self._make_card(idx, loc)
            self._list_layout.add_widget(card)

    def _make_card(self, index, loc):
        """Build a card widget for a single saved location."""
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=120,
            padding=Sizing.PADDING_SM,
        )

        with card.canvas.before:
            Color(*Colors.BG_CARD)
            bg = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[Sizing.BORDER_RADIUS]
            )
        card.bind(
            pos=lambda inst, val, b=bg: setattr(b, "pos", val),
            size=lambda inst, val, b=bg: setattr(b, "size", val),
        )

        # coords line
        coords_text = f"{loc.dest_lat:.6f}, {loc.dest_lon:.6f}"
        coords_lbl = Label(
            text=coords_text,
            font_size=Sizing.FONT_BODY,
            color=Colors.TEXT_PRIMARY,
            bold=True,
            halign="left",
            size_hint_y=None,
            height=28,
        )
        coords_lbl.bind(size=coords_lbl.setter("text_size"))
        card.add_widget(coords_lbl)

        # details line
        details = (
            f"Bearing: {loc.bearing:.0f}°  |  "
            f"Distance: {loc.distance:.0f}m  |  "
            f"±{loc.accuracy:.0f}m"
        )
        details_lbl = Label(
            text=details,
            font_size=Sizing.FONT_SMALL,
            color=Colors.TEXT_SECONDARY,
            halign="left",
            size_hint_y=None,
            height=22,
        )
        details_lbl.bind(size=details_lbl.setter("text_size"))
        card.add_widget(details_lbl)

        # timestamp
        ts_lbl = Label(
            text=loc.timestamp[:19].replace("T", "  "),  # trim microseconds
            font_size=Sizing.FONT_SMALL,
            color=Colors.TEXT_HINT,
            halign="left",
            size_hint_y=None,
            height=20,
        )
        ts_lbl.bind(size=ts_lbl.setter("text_size"))
        card.add_widget(ts_lbl)

        # action buttons row
        actions = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=34,
            spacing=Sizing.PADDING_SM,
        )

        open_btn = Button(
            text="Open Map",
            font_size=Sizing.FONT_SMALL,
            color=Colors.ACCENT,
            background_normal="",
            background_color=(0, 0, 0, 0),
            size_hint_x=0.5,
        )
        open_btn.bind(on_release=lambda btn, la=loc.dest_lat, lo=loc.dest_lon:
                       self._open_in_maps(la, lo))

        del_btn = Button(
            text="Delete",
            font_size=Sizing.FONT_SMALL,
            color=Colors.ACCENT_ERROR,
            background_normal="",
            background_color=(0, 0, 0, 0),
            size_hint_x=0.5,
        )
        del_btn.bind(on_release=lambda btn, i=index: self._delete_entry(i))

        actions.add_widget(open_btn)
        actions.add_widget(del_btn)
        card.add_widget(actions)

        return card

    def _open_in_maps(self, lat, lon):
        url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        try:
            webbrowser.open(url)
        except Exception as e:
            Logger.warning(f"HistoryScreen: maps open failed - {e}")

    def _delete_entry(self, index):
        self.app.repo.delete(index)
        self._refresh_list()
