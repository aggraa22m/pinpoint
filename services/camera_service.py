"""Camera preview service.

On mobile we use Kivy's Camera widget which wraps platform camera APIs.
On desktop it'll try to use a webcam — if none is available we show
a placeholder gradient instead.
"""
from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.logger import Logger


class CameraPreview(Camera):
    """Camera widget with crosshair overlay.

    Extends Kivy's built-in Camera to add a targeting reticle on top.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("resolution", (640, 480))
        kwargs.setdefault("play", False)
        super().__init__(**kwargs)
        self._crosshair_binds_done = False

    def start(self):
        self.play = True
        if not self._crosshair_binds_done:
            self.bind(size=self._draw_crosshair, pos=self._draw_crosshair)
            Clock.schedule_once(lambda dt: self._draw_crosshair(), 0.5)
            self._crosshair_binds_done = True

    def stop(self):
        self.play = False

    def _draw_crosshair(self, *args):
        # clear old crosshair graphics
        self.canvas.after.clear()
        cx = self.center_x
        cy = self.center_y

        with self.canvas.after:
            # outer ring
            Color(1, 1, 1, 0.6)
            r = 40
            Line(circle=(cx, cy, r), width=1.5)

            # inner dot
            Color(1, 0.2, 0.2, 0.8)
            dot_r = 4
            Ellipse(pos=(cx - dot_r, cy - dot_r), size=(dot_r * 2, dot_r * 2))

            # crosshair lines
            Color(1, 1, 1, 0.4)
            gap = 15
            line_len = 25
            # top
            Line(points=[cx, cy + gap, cx, cy + gap + line_len], width=1.2)
            # bottom
            Line(points=[cx, cy - gap, cx, cy - gap - line_len], width=1.2)
            # left
            Line(points=[cx - gap, cy, cx - gap - line_len, cy], width=1.2)
            # right
            Line(points=[cx + gap, cy, cx + gap + line_len, cy], width=1.2)


class FallbackPreview(Widget):
    """Shown when camera isn't available (e.g., no webcam on desktop).

    Just a dark background with the crosshair so the UI still works.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._redraw, pos=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw(), 0.1)

    def start(self):
        pass

    def stop(self):
        pass

    def _redraw(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y

        with self.canvas:
            # dark background
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)

            # grid lines for visual interest
            Color(0.15, 0.15, 0.2, 0.5)
            step = 50
            for x in range(int(self.x), int(self.right), step):
                Line(points=[x, self.y, x, self.top], width=0.5)
            for y in range(int(self.y), int(self.top), step):
                Line(points=[self.x, y, self.right, y], width=0.5)

            # label
            Color(1, 1, 1, 0.3)

        with self.canvas.after:
            # crosshair (same as CameraPreview)
            Color(1, 1, 1, 0.6)
            r = 40
            Line(circle=(cx, cy, r), width=1.5)

            Color(1, 0.2, 0.2, 0.8)
            dot_r = 4
            Ellipse(pos=(cx - dot_r, cy - dot_r), size=(dot_r * 2, dot_r * 2))

            Color(1, 1, 1, 0.4)
            gap = 15
            line_len = 25
            Line(points=[cx, cy + gap, cx, cy + gap + line_len], width=1.2)
            Line(points=[cx, cy - gap, cx, cy - gap - line_len], width=1.2)
            Line(points=[cx - gap, cy, cx - gap - line_len, cy], width=1.2)
            Line(points=[cx + gap, cy, cx + gap + line_len, cy], width=1.2)


def create_camera_widget(**kwargs):
    """Factory function — tries real camera, falls back to placeholder.

    Kivy's Camera widget will throw if no camera provider is available,
    so we catch that and use our grid-based fallback instead.
    """
    # filter out kwargs that FallbackPreview doesn't understand
    fallback_kwargs = {k: v for k, v in kwargs.items()
                       if k in ("size_hint", "pos_hint", "size", "pos")}
    try:
        cam = CameraPreview(**kwargs)
        cam.play = True
        Clock.schedule_once(lambda dt: None, 0.1)
        Logger.info("CameraService: using real camera")
        return cam
    except Exception as e:
        Logger.warning(f"CameraService: camera unavailable ({e}), using fallback")
        return FallbackPreview(**fallback_kwargs)
