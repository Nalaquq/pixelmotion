"""Kernels and the sliding-window convolution animation."""

from fractions import Fraction

import numpy as np

from ..animation.base import Animation
from ..basics.shapes import Rectangle
from ..basics.text import Text
from ..image.grids import PixelGrid
from ..rate_functions import linear
from ..theme import ACCENT, ORANGE, PANEL_BG, TEXT


def correlate_valid(image, kernel):
    """Sliding-window sum of products (what CV libraries call "convolution")."""
    H, W = image.shape
    kh, kw = kernel.shape
    out = np.empty((H - kh + 1, W - kw + 1))
    for r in range(out.shape[0]):
        for c in range(out.shape[1]):
            out[r, c] = np.sum(image[r:r + kh, c:c + kw] * kernel)
    return out


class Kernel(PixelGrid):
    """A filter kernel: a grid with a flat background and its weights shown.

    ``fractions=True`` prints weights like ``1/9`` instead of ``0.111``.
    ``scale`` pulls a common factor outside the grid, e.g.
    ``Kernel(np.ones((3, 3)), scale="1/9")`` shows ones with "1/9 ×" beside
    them; ``kernel.values`` still includes the factor.
    """

    def __init__(self, values, cell=0.55, fractions=False, scale=None, fill=PANEL_BG,
                 border_color=ACCENT, fmt="{:g}", **kwargs):
        shown = np.array(values, float)
        factor = 1.0 if scale is None else float(Fraction(scale))
        super().__init__(shown * factor, cell=cell, cmap=None, fill=fill,
                         border_color=border_color, fmt=fmt, **kwargs)
        self.shown = shown
        self.fractions = fractions
        self.scale = scale

    def display_values(self):
        return self.shown if self.scale is not None else self.values

    def format_value(self, v):
        if self.fractions:
            return str(Fraction(v).limit_denominator(64)).replace("-", "−")
        return super().format_value(v)

    def draw(self, ctx, alpha, progress):
        super().draw(ctx, alpha, progress)
        if self.scale is not None:
            x0, y0, x1, y1 = self.cell_box(0, 0, *self.shape)
            ctx.ax.text(x0 - 0.12, (y0 + y1) / 2, f"{self.scale} ×", fontsize=16,
                        color=TEXT, weight="bold", ha="right", va="center", alpha=alpha)


class Convolve(Animation):
    """Slide ``kernel``'s window over ``image``, filling ``output`` cell by cell.

    Parameters
    ----------
    image, kernel, output : PixelGrid
        ``output`` should have the "valid" shape ``(H-kh+1, W-kw+1)``; create
        it with ``PixelGrid.empty(shape, ...)`` so cells start blank.
    cells : list of (r, c), optional
        Which output cells to visit (default: all, in reading order).
    time_per_cell : float
        Seconds the window rests on each position (default 0.5).
    flip : bool
        Flip the kernel first (true convolution) instead of correlation.
    show_sum : bool
        Show "sum = value" beneath the output while sweeping.

    Notes
    -----
    The window outlines are added for the sweep and removed afterwards.
    """

    def __init__(self, image, kernel, output, cells=None, time_per_cell=0.5,
                 window_color=ORANGE, flip=False, show_sum=True, **kwargs):
        k = kernel.values[::-1, ::-1] if flip else kernel.values
        self.result = correlate_valid(np.nan_to_num(image.values), k)
        if cells is None:
            cells = [(r, c) for r in range(self.result.shape[0])
                     for c in range(self.result.shape[1])]
        self.cells = list(cells)
        kwargs.setdefault("run_time", time_per_cell * len(self.cells))
        super().__init__(output, rate_func=linear, **kwargs)
        self.image, self.kernel, self.output = image, kernel, output
        self.window_color = window_color
        self.show_sum = show_sum

    def begin(self, scene):
        kh, kw = self.kernel.shape
        self.win_in = Rectangle.from_corners(*self.image.cell_box(0, 0, kh, kw),
                                             color=self.window_color, stroke=4, z=5)
        self.win_out = Rectangle.from_corners(*self.output.cell_box(0, 0),
                                              color=self.window_color, stroke=4, z=5)
        x0, y0, x1, _ = self.output.cell_box(self.output.shape[0] - 1, 0, 1,
                                             self.output.shape[1])
        self.readout = Text("", pos=((x0 + x1) / 2, y0 - 0.35), size=14, color=TEXT,
                            va="top", weight="bold")
        scene.add(self.win_in, self.win_out)
        if self.show_sum:
            scene.add(self.readout)
        self._scene = scene
        super().begin(scene)

    def interpolate(self, alpha):
        n = len(self.cells)
        idx = min(int(alpha * n), n - 1)
        r, c = self.cells[idx]
        kh, kw = self.kernel.shape
        self.win_in.move_to(Rectangle.from_corners(*self.image.cell_box(r, c, kh, kw)))
        self.win_out.move_to(Rectangle.from_corners(*self.output.cell_box(r, c)))
        vals = self.output.values.copy()
        for rr, cc in self.cells[:idx + 1]:
            vals[rr, cc] = self.result[rr, cc]
        self.output.values = vals
        v = self.result[r, c]
        self.readout.set_text(f"sum(window × kernel) = {self.output.format_value(v)}")

    def finish(self, scene):
        super().finish(scene)
        scene.remove(self.win_in, self.win_out, self.readout)
