"""Main camera screen — the primary interface.

Full-screen camera preview with crosshair overlay, heading display,
GPS accuracy badge, distance input, and action buttons.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger

from presentation.theme import Colors, Sizing
from presentation.widgets.heading_display import HeadingDisplay
from presentation.widgets.accuracy_indicator import AccuracyIndicator
from presentation.widgets.styled_button import PrimaryButton, SecondaryButton
from services.camera_service import create_camera_widget


class CameraScreen(Screen):
    """Main app screen with camera viewfinder and controls."""

    def __init__(self, app_ref, **kwargs):
        super().__init__(name="camera", **kwargs)
        self.app = app_ref
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        # -- camera preview (fills entire screen) --
        try:
            self._camera = create_camera_widget(
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0},
            )
        except Exception as e:
            Logger.warning(f"CameraScreen: camera init failed - {e}")
            from services.camera_service import FallbackPreview
            self._camera = FallbackPreview(
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0},
            )
        root.add_widget(self._camera)

        # -- top overlay: heading + accuracy --
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=70,
            pos_hint={"top": 1},
            padding=[Sizing.PADDING, Sizing.PADDING_SM],
            spacing=Sizing.PADDING,
        )

        self._heading_display = HeadingDisplay()
        self._accuracy_indicator = AccuracyIndicator()

        # spacer pushes accuracy to the right
        top_bar.add_widget(self._accuracy_indicator)
        top_bar.add_widget(Label(size_hint_x=1))  # flex spacer
        top_bar.add_widget(self._heading_display)

        root.add_widget(top_bar)

        # -- tilt warning (hidden by default) --
        self._tilt_label = Label(
            text="Phone is tilted — hold level for best accuracy",
            font_size=Sizing.FONT_SMALL,
            color=Colors.ACCENT_WARN,
            size_hint=(1, None),
            height=30,
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            opacity=0,
        )
        root.add_widget(self._tilt_label)

        # -- bottom controls panel --
        # taller on desktop to fit lat/lon inputs
        is_desktop = platform not in ("android", "ios")
        panel_height = 300 if is_desktop else 200

        bottom = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=panel_height,
            pos_hint={"y": 0},
            padding=[Sizing.PADDING_LG, Sizing.PADDING],
            spacing=Sizing.PADDING_SM,
        )

        # semi-transparent background for bottom panel
        with bottom.canvas.before:
            Color(0, 0, 0, 0.65)
            self._bottom_bg = RoundedRectangle(
                pos=bottom.pos, size=bottom.size,
                radius=[Sizing.BORDER_RADIUS, Sizing.BORDER_RADIUS, 0, 0],
            )
        bottom.bind(
            pos=lambda *a: setattr(self._bottom_bg, "pos", bottom.pos),
            size=lambda *a: setattr(self._bottom_bg, "size", bottom.size),
        )

        # on desktop: manual lat/lon entry since there's no real GPS
        if is_desktop:
            loc_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=Sizing.BUTTON_HEIGHT,
                spacing=Sizing.PADDING_SM,
            )

            loc_row.add_widget(Label(
                text="Lat:",
                font_size=Sizing.FONT_BODY,
                color=Colors.TEXT_SECONDARY,
                size_hint_x=0.15,
            ))
            self._lat_input = TextInput(
                text="0.0",
                multiline=False,
                font_size=Sizing.FONT_BODY,
                foreground_color=Colors.TEXT_PRIMARY,
                background_color=Colors.INPUT_BG,
                cursor_color=Colors.ACCENT,
                padding=[12, 10],
                size_hint_x=0.35,
            )
            loc_row.add_widget(self._lat_input)

            loc_row.add_widget(Label(
                text="Lon:",
                font_size=Sizing.FONT_BODY,
                color=Colors.TEXT_SECONDARY,
                size_hint_x=0.15,
            ))
            self._lon_input = TextInput(
                text="0.0",
                multiline=False,
                font_size=Sizing.FONT_BODY,
                foreground_color=Colors.TEXT_PRIMARY,
                background_color=Colors.INPUT_BG,
                cursor_color=Colors.ACCENT,
                padding=[12, 10],
                size_hint_x=0.35,
            )
            loc_row.add_widget(self._lon_input)

            bottom.add_widget(loc_row)

            set_loc_btn = SecondaryButton(
                text="SET MY LOCATION",
                size_hint_y=None,
                height=38,
            )
            set_loc_btn.bind(on_release=self._on_set_location)
            bottom.add_widget(set_loc_btn)

        # distance input row
        dist_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=Sizing.BUTTON_HEIGHT,
            spacing=Sizing.PADDING_SM,
        )

        dist_label = Label(
            text="Distance (m):",
            font_size=Sizing.FONT_BODY,
            color=Colors.TEXT_SECONDARY,
            size_hint_x=0.4,
            halign="left",
        )

        self._distance_input = TextInput(
            text="100",
            multiline=False,
            input_filter="float",
            font_size=Sizing.FONT_BODY,
            foreground_color=Colors.TEXT_PRIMARY,
            background_color=Colors.INPUT_BG,
            cursor_color=Colors.ACCENT,
            padding=[12, 10],
            size_hint_x=0.6,
        )

        dist_row.add_widget(dist_label)
        dist_row.add_widget(self._distance_input)
        bottom.add_widget(dist_row)

        # coordinate display (shows current position)
        self._coords_label = Label(
            text="Acquiring GPS...",
            font_size=Sizing.FONT_SMALL,
            color=Colors.TEXT_HINT,
            size_hint_y=None,
            height=24,
        )
        bottom.add_widget(self._coords_label)

        # buttons row
        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=Sizing.BUTTON_HEIGHT,
            spacing=Sizing.PADDING,
        )

        locate_btn = PrimaryButton(text="LOCATE OBJECT", size_hint_x=0.65)
        locate_btn.bind(on_release=self._on_locate)

        history_btn = SecondaryButton(text="HISTORY", size_hint_x=0.35)
        history_btn.bind(on_release=self._on_history)

        btn_row.add_widget(locate_btn)
        btn_row.add_widget(history_btn)
        bottom.add_widget(btn_row)

        root.add_widget(bottom)
        self.add_widget(root)

        # update sensor readings on a timer
        Clock.schedule_interval(self._update_display, 1 / 10)

    def on_enter(self):
        self._camera.start()

    def on_leave(self):
        self._camera.stop()

    def _update_display(self, dt):
        loc = self.app.location_svc
        compass = self.app.compass_svc
        sensors = self.app.sensor_svc

        # update heading
        self._heading_display.heading = compass.heading
        self._heading_display.cardinal = compass.cardinal

        # update accuracy
        self._accuracy_indicator.accuracy = loc.accuracy

        # update coords display
        if loc.is_active:
            self._coords_label.text = (
                f"{loc.latitude:.6f}, {loc.longitude:.6f}"
            )
        else:
            self._coords_label.text = "Acquiring GPS..."

        # tilt warning
        if not sensors.tilt_ok:
            self._tilt_label.opacity = 1
        else:
            self._tilt_label.opacity = 0

    def _validate_distance(self):
        """Returns distance as float or None if invalid."""
        text = self._distance_input.text.strip()
        if not text:
            return None
        try:
            val = float(text)
            if val <= 0:
                return None
            return val
        except ValueError:
            return None

    def _on_set_location(self, *args):
        """Desktop only — apply manually entered lat/lon."""
        try:
            lat = float(self._lat_input.text.strip())
            lon = float(self._lon_input.text.strip())
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                self._show_error("Lat must be -90 to 90, Lon -180 to 180")
                return
            self.app.location_svc.set_manual_location(lat, lon)
        except (ValueError, AttributeError):
            self._show_error("Enter valid lat/lon numbers")

    def _on_locate(self, *args):
        distance = self._validate_distance()
        if distance is None:
            self._show_error("Enter a valid distance (positive number)")
            return

        loc = self.app.location_svc
        if not loc.is_active:
            self._show_error("GPS not available")
            return

        bearing = self.app.compass_svc.heading

        # run the calculation
        calc = self.app.calculator
        dest_lat, dest_lon = calc.calculate_destination(
            loc.latitude, loc.longitude, bearing, distance
        )
        accuracy = calc.estimate_accuracy(loc.accuracy, distance)

        # pass result to result screen
        self.app.last_result = {
            "src_lat": loc.latitude,
            "src_lon": loc.longitude,
            "dest_lat": dest_lat,
            "dest_lon": dest_lon,
            "bearing": bearing,
            "distance": distance,
            "accuracy": accuracy,
        }

        self.manager.current = "result"

    def _on_history(self, *args):
        self.manager.current = "history"

    def _show_error(self, msg):
        """Quick visual feedback for errors — flash the coords label red."""
        self._coords_label.text = msg
        self._coords_label.color = Colors.ACCENT_ERROR
        Clock.schedule_once(
            lambda dt: setattr(self._coords_label, "color", Colors.TEXT_HINT),
            2.0,
        )
