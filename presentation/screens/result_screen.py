"""Result screen — shows the calculated object coordinates.

Card-based layout with coordinate details, map link, and action buttons.
"""
import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.logger import Logger

from presentation.theme import Colors, Sizing
from presentation.widgets.styled_button import PrimaryButton, SecondaryButton
from data.location_repository import SavedLocation


class ResultScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="result", **kwargs)
        self.app = app_ref
        self._build_ui()

    def _build_ui(self):
        # main vertical layout with dark background
        root = BoxLayout(
            orientation="vertical",
            padding=Sizing.PADDING_LG,
            spacing=Sizing.PADDING,
        )

        with root.canvas.before:
            Color(*Colors.BG_PRIMARY)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda *a: setattr(self._bg, "pos", root.pos),
            size=lambda *a: setattr(self._bg, "size", root.size),
        )

        # title
        title = Label(
            text="Object Location",
            font_size=Sizing.FONT_HEADING,
            color=Colors.TEXT_PRIMARY,
            bold=True,
            size_hint_y=None,
            height=50,
        )
        root.add_widget(title)

        # -- result card --
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=280,
            padding=Sizing.PADDING,
            spacing=Sizing.PADDING_SM,
        )
        with card.canvas.before:
            Color(*Colors.BG_CARD)
            self._card_bg = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[Sizing.BORDER_RADIUS]
            )
        card.bind(
            pos=lambda *a: setattr(self._card_bg, "pos", card.pos),
            size=lambda *a: setattr(self._card_bg, "size", card.size),
        )

        # coordinate fields
        self._lat_label = self._make_field("Latitude", "—")
        self._lon_label = self._make_field("Longitude", "—")
        self._bearing_label = self._make_field("Bearing", "—")
        self._distance_label = self._make_field("Distance", "—")
        self._accuracy_label = self._make_field("Est. Accuracy", "—")

        card.add_widget(self._lat_label)
        card.add_widget(self._lon_label)
        card.add_widget(self._bearing_label)
        card.add_widget(self._distance_label)
        card.add_widget(self._accuracy_label)

        root.add_widget(card)

        # -- source info (where the user was standing) --
        self._source_label = Label(
            text="",
            font_size=Sizing.FONT_SMALL,
            color=Colors.TEXT_HINT,
            size_hint_y=None,
            height=30,
        )
        root.add_widget(self._source_label)

        # spacer
        root.add_widget(Label(size_hint_y=1))

        # -- action buttons --
        btn_grid = GridLayout(
            cols=2,
            size_hint_y=None,
            height=Sizing.BUTTON_HEIGHT * 2 + Sizing.PADDING_SM,
            spacing=Sizing.PADDING_SM,
        )

        maps_btn = PrimaryButton(text="OPEN IN MAPS")
        maps_btn.bind(on_release=self._open_maps)

        save_btn = PrimaryButton(
            text="SAVE LOCATION",
            bg_color=Colors.ACCENT_SUCCESS,
        )
        save_btn.bind(on_release=self._save_location)

        copy_btn = SecondaryButton(text="COPY COORDS")
        copy_btn.bind(on_release=self._copy_coords)

        back_btn = SecondaryButton(text="BACK")
        back_btn.bind(on_release=self._go_back)

        btn_grid.add_widget(maps_btn)
        btn_grid.add_widget(save_btn)
        btn_grid.add_widget(copy_btn)
        btn_grid.add_widget(back_btn)

        root.add_widget(btn_grid)
        self.add_widget(root)

    def _make_field(self, label_text, value_text):
        """Helper to create a labeled value row."""
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
        )
        lbl = Label(
            text=label_text,
            font_size=Sizing.FONT_BODY,
            color=Colors.TEXT_SECONDARY,
            halign="left",
            size_hint_x=0.4,
        )
        lbl.bind(size=lbl.setter("text_size"))

        val = Label(
            text=value_text,
            font_size=Sizing.FONT_BODY,
            color=Colors.TEXT_PRIMARY,
            bold=True,
            halign="right",
            size_hint_x=0.6,
        )
        val.bind(size=val.setter("text_size"))

        row.add_widget(lbl)
        row.add_widget(val)
        row._value_label = val  # stash reference for updating later
        return row

    def on_enter(self):
        result = self.app.last_result
        if not result:
            return

        lat = result["dest_lat"]
        lon = result["dest_lon"]

        self._lat_label._value_label.text = f"{lat:.6f}°"
        self._lon_label._value_label.text = f"{lon:.6f}°"
        self._bearing_label._value_label.text = f"{result['bearing']:.1f}°"
        self._distance_label._value_label.text = f"{result['distance']:.0f} m"
        self._accuracy_label._value_label.text = f"±{result['accuracy']:.0f} m"

        # set accuracy color
        acc = result["accuracy"]
        if acc < 50:
            color = Colors.ACCENT_SUCCESS
        elif acc < 200:
            color = Colors.ACCENT_WARN
        else:
            color = Colors.ACCENT_ERROR
        self._accuracy_label._value_label.color = color

        self._source_label.text = (
            f"From: {result['src_lat']:.6f}, {result['src_lon']:.6f}"
        )

    def _open_maps(self, *args):
        result = self.app.last_result
        if not result:
            return
        lat, lon = result["dest_lat"], result["dest_lon"]
        # google maps URL works on both desktop and mobile
        url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        try:
            webbrowser.open(url)
        except Exception as e:
            Logger.warning(f"ResultScreen: couldn't open maps - {e}")

    def _save_location(self, *args):
        result = self.app.last_result
        if not result:
            return

        loc = SavedLocation(
            src_lat=result["src_lat"],
            src_lon=result["src_lon"],
            dest_lat=result["dest_lat"],
            dest_lon=result["dest_lon"],
            bearing=result["bearing"],
            distance=result["distance"],
            accuracy=result["accuracy"],
        )
        self.app.repo.add(loc)
        Logger.info("ResultScreen: location saved")

        # visual feedback — briefly change button text
        for child in self.children[0].children:
            if hasattr(child, "children"):
                for btn in child.children:
                    if hasattr(btn, "text") and btn.text == "SAVE LOCATION":
                        btn.text = "SAVED!"
                        Clock.schedule_once(
                            lambda dt: setattr(btn, "text", "SAVE LOCATION"), 1.5
                        )
                        break

    def _copy_coords(self, *args):
        result = self.app.last_result
        if not result:
            return
        text = f"{result['dest_lat']:.6f}, {result['dest_lon']:.6f}"
        try:
            Clipboard.copy(text)
        except Exception:
            pass

    def _go_back(self, *args):
        self.manager.current = "camera"
