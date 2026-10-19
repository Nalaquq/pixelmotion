"""Step-by-step animations of Canny's thinning and edge-linking stages."""

import numpy as np

from ..animation.base import Animation
from ..basics.shapes import Line, Rectangle
from ..basics.text import Text
from ..rate_functions import linear
from ..theme import ACCENT, GRAY, GREEN, ORANGE, RED, TEXT
from .ops import NONE, STRONG, WEAK, hysteresis_waves, nms_neighbors


class NonMaxSuppression(Animation):
    """Visit pixels of a gradient-magnitude grid, compare each with its two
    neighbours along the gradient, and keep it only if it is the largest.

    Parameters
    ----------
    magnitude : PixelGrid
        Gradient magnitudes (the input).
    angle : 2-D array
        Gradient direction in degrees at each pixel (``edges.gradient_direction``).
    output : PixelGrid
        Same shape as ``magnitude``; use ``PixelGrid.empty(shape)``. Kept
        pixels get their magnitude, suppressed ones get 0.
    cells : list of (r, c), optional
        Pixels to visit (default: every interior pixel in reading order).
    time_per_cell : float
        Seconds spent on each pixel.
    show_reason : bool
        Show the comparison ("87 > 64 and 87 >= 51: keep") under the output.

    Notes
    -----
    The center box is orange; the two neighbours it is compared with are
    blue, joined by a dashed line along the gradient. The boxes and readout
    are removed when the sweep ends.
    """

    def __init__(self, magnitude, angle, output, cells=None, time_per_cell=0.8,
                 show_reason=True, **kwargs):
        H, W = magnitude.shape
        self.angle = np.asarray(angle, float)
        if cells is None:
            cells = [(r, c) for r in range(1, H - 1) for c in range(1, W - 1)]
        self.cells = list(cells)
        kwargs.setdefault("run_time", time_per_cell * len(self.cells))
        super().__init__(output, rate_func=linear, **kwargs)
        self.magnitude, self.output = magnitude, output
        self.show_reason = show_reason

    def _decide(self, r, c):
        m = self.magnitude.values
        (r1, c1), (r2, c2) = nms_neighbors(r, c, self.angle[r, c])
        a, b, v = m[r1, c1], m[r2, c2], m[r, c]
        keep = v > a and v >= b
        return keep, (r1, c1), (r2, c2), a, b, v

    def begin(self, scene):
        g = self.magnitude
        self.center_box = Rectangle.from_corners(*g.cell_box(0, 0), color=ORANGE, stroke=4, z=6)
        self.nbr_boxes = [Rectangle.from_corners(*g.cell_box(0, 0), color=ACCENT, stroke=4, z=6)
                          for _ in range(2)]
        self.out_box = Rectangle.from_corners(*self.output.cell_box(0, 0), color=ORANGE,
                                              stroke=4, z=6)
        self.direction = Line((0, 0), (1, 0), color=GRAY, stroke=2, dashed=True, z=5)
        self.direction.check_labels = False      # it deliberately crosses the cell values
        x0, y0, x1, _ = self.output.cell_box(self.output.shape[0] - 1, 0, 1, self.output.shape[1])
        self.readout = Text("", pos=((x0 + x1) / 2, y0 - 0.35), size=14, weight="bold",
                            va="top", color=TEXT)
        self.extras = [self.direction, self.center_box, *self.nbr_boxes, self.out_box]
        if self.show_reason:
            self.extras.append(self.readout)
        scene.add(*self.extras)
        super().begin(scene)

    def interpolate(self, alpha):
        n = len(self.cells)
        idx = min(int(alpha * n), n - 1)
        r, c = self.cells[idx]
        g = self.magnitude
        keep, p1, p2, a, b, v = self._decide(r, c)
        self.center_box.move_to(Rectangle.from_corners(*g.cell_box(r, c)))
        for box, (rr, cc) in zip(self.nbr_boxes, (p1, p2)):
            box.move_to(Rectangle.from_corners(*g.cell_box(rr, cc)))
        self.direction.points = np.array([g.cell_center(*p1), g.cell_center(*p2)])
        self.out_box.move_to(Rectangle.from_corners(*self.output.cell_box(r, c)))
        self.out_box.color = GREEN if keep else RED
        vals = self.output.values.copy()
        for rr, cc in self.cells[:idx + 1]:
            k, *_ = self._decide(rr, cc)
            vals[rr, cc] = g.values[rr, cc] if k else 0.0
        self.output.values = vals
        f = g.format_value
        if keep:
            self.readout.set_text(f"{f(v)} > {f(a)} and {f(v)} ≥ {f(b)}:  keep")
            self.readout.color = GREEN
        else:
            self.readout.set_text(f"{f(max(a, b))} is stronger:  suppress")
            self.readout.color = RED

    def finish(self, scene):
        super().finish(scene)
        scene.remove(*self.extras)


class Hysteresis(Animation):
    """Grow strong edges into touching weak pixels, one ring per step, then
    drop the weak pixels that never connected.

    Parameters
    ----------
    labels : PixelGrid
        A grid of 0 / 1 / 2 (none / weak / strong), e.g. drawn with
        ``cmap="labels"``. Its values change as the edges grow.
    time_per_wave : float
        Seconds per growth step.
    drop_weak : bool
        Finish by turning unconnected weak pixels off.
    """

    def __init__(self, labels, time_per_wave=0.8, drop_weak=True, **kwargs):
        self.waves = hysteresis_waves(labels.values.astype(int))
        self.drop_weak = drop_weak
        steps = len(self.waves) - 1 + (1 if drop_weak else 0)
        kwargs.setdefault("run_time", time_per_wave * max(steps, 1))
        super().__init__(labels, rate_func=linear, **kwargs)
        final = self.waves[-1].copy()
        final[final == WEAK] = NONE
        self.sequence = self.waves[1:] + ([final] if drop_weak else [])
        self.steps = max(len(self.sequence), 1)

    def interpolate(self, alpha):
        if not self.sequence:
            return
        idx = min(int(alpha * self.steps), self.steps - 1)
        if alpha <= 0:
            self.mobject.values = self.waves[0].astype(float)
        else:
            self.mobject.values = self.sequence[idx].astype(float)

