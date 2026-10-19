"""Turn a list of mobjects into one rendered frame."""

from contextlib import contextmanager

import matplotlib
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.text import Text
from PIL import Image


def _identity(points):
    return points


class RenderContext:
    """What a mobject sees while drawing.

    ``ax`` is the axes to draw on: the full-figure canvas (units = inches,
    origin bottom-left) or a panel's own axes (e.g. a Plane's data space).
    ``tf`` maps the mobject's points into ``ax`` data coords; a Plane uses it
    to apply its linear transform to everything inside it.
    """

    def __init__(self, fig, theme):
        self.fig = fig
        self.theme = theme
        self.tf = _identity
        self.segments = []        # (ax, Nx2 data points, label) for overlap checks
        self.drawn_texts = []     # every Text actually painted in this frame
        self._canvas = None
        self._n_axes = 0
        self.ax = self.canvas

    @property
    def canvas(self):
        """The topmost full-figure canvas; a new one is stacked above any panel
        drawn since, so later mobjects paint over earlier panels."""
        if self._canvas is None:
            ax = self._add_axes([0, 0, 1, 1])
            ax.set_xlim(0, self.theme.width)
            ax.set_ylim(0, self.theme.height)
            ax.set_autoscale_on(False)   # imshow etc. must not move the canvas
            ax.axis("off")
            ax.patch.set_alpha(0)
            self._canvas = ax
        return self._canvas

    @property
    def on_canvas(self):
        """True when drawing straight onto the canvas (units = inches)."""
        return self.ax is self._canvas and self.tf is _identity

    def _add_axes(self, frac_rect, **kwargs):
        ax = self.fig.add_axes(frac_rect, **kwargs)
        ax.set_zorder(self._n_axes)
        self._n_axes += 1
        return ax

    def new_axes(self, rect, **kwargs):
        """Axes covering ``rect`` = (x, y, w, h) in canvas units."""
        x, y, w, h = rect
        W, H = self.theme.width, self.theme.height
        ax = self._add_axes([x / W, y / H, w / W, h / H], **kwargs)
        self._canvas = None
        return ax

    @contextmanager
    def using(self, ax, tf=None):
        """Draw children into ``ax`` (with point transform ``tf``)."""
        prev_ax, prev_tf = self.ax, self.tf
        on_canvas = prev_ax is self._canvas
        self.ax, self.tf = ax, (tf or _identity)
        try:
            yield ax
        finally:
            self.tf = prev_tf
            self.ax = self.canvas if on_canvas else prev_ax

    def register_segments(self, points, label=""):
        """Record a drawn polyline (data coords of ``ax``) for label checks."""
        self.segments.append((self.ax, np.asarray(points, float), label))


@contextmanager
def _recording_texts(out):
    """Record each Text matplotlib paints. Tick labels outside the view
    still exist as objects but are never drawn, so this is the only reliable
    list of what is on screen."""
    original = Text.draw

    def draw(self, renderer):
        out.append(self)
        return original(self, renderer)
    Text.draw = draw
    try:
        yield
    finally:
        Text.draw = original


class FrameRenderer:
    def __init__(self, theme, dpi=None):
        self.theme = theme
        self.fig = Figure(figsize=(theme.width, theme.height),
                          dpi=dpi or theme.dpi, facecolor=theme.bg)
        FigureCanvasAgg(self.fig)
        self.rc = {
            "font.family": theme.font_family,
            "mathtext.fontset": "dejavusans",
            "axes.unicode_minus": True,
        }

    def draw(self, mobjects):
        """Render ``mobjects``; returns the RenderContext (for overlap checks)."""
        with matplotlib.rc_context(self.rc):
            self.fig.clear()
            ctx = RenderContext(self.fig, self.theme)
            for m in sorted(mobjects, key=lambda m: m.z):
                ctx.ax = ctx.canvas
                m.render(ctx)
            with _recording_texts(ctx.drawn_texts):
                self.fig.canvas.draw()
        return ctx

    def image(self):
        buf = np.asarray(self.fig.canvas.buffer_rgba())
        return Image.fromarray(buf[..., :3].copy())

    @property
    def renderer(self):
        return self.fig.canvas.get_renderer()
