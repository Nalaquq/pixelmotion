"""Drawable edge concepts: gradient arrows, one-pixel gradient diagrams,
and 1-D intensity profiles with their derivatives."""

import numpy as np
from matplotlib import colormaps
from matplotlib.patches import Arc, FancyArrowPatch
from matplotlib.ticker import MaxNLocator

from ..core.mobject import Mobject
from ..theme import ACCENT, ACCENT2, DEFAULT_THEME, GREEN, ORANGE, PURPLE, SUB, TEXT


class GradientField(Mobject):
    """Arrows showing the gradient (direction of fastest brightening).

    Lay it over an :class:`ImagePanel` with :meth:`over` so the arrows line
    up with the pixels.

    Parameters
    ----------
    gx, gy : 2-D arrays
        Horizontal and vertical gradients (e.g. from ``edges.sobel``), with
        image rows growing downward.
    rect : Region or (x, y, w, h)
        Canvas area of the image the arrows sit on.
    step : int
        Draw one arrow every ``step`` pixels.
    normalize : bool
        All arrows the same length (direction only) instead of scaled by
        gradient strength.
    min_strength : float
        Hide arrows weaker than this fraction of the strongest.
    color : color or "magnitude"
        One color, or color arrows by strength.

    Notes
    -----
    ``Create`` grows the arrows from their tails.
    """

    def __init__(self, gx, gy, rect, step=6, normalize=False, min_strength=0.15, color=ORANGE,
                 arrow_width=0.006, **kwargs):
        super().__init__(**kwargs)
        gx, gy = np.asarray(gx, float), np.asarray(gy, float)
        self.image_shape = gx.shape
        self.rect = np.array(getattr(rect, "rect", rect), float)
        H, W = gx.shape
        rows = np.arange(step // 2, H, step)
        cols = np.arange(step // 2, W, step)
        R, C = np.meshgrid(rows, cols, indexing="ij")
        u, v = gx[R, C], gy[R, C]
        mag = np.hypot(u, v)
        peak = mag.max() or 1.0
        keep = mag >= min_strength * peak
        length = np.where(normalize, 0.8 * step, 0.95 * step * mag / peak)
        with np.errstate(invalid="ignore", divide="ignore"):
            self.U = np.where(keep, u / np.maximum(mag, 1e-12) * length, 0.0)
            self.V = np.where(keep, v / np.maximum(mag, 1e-12) * length, 0.0)
        self.X, self.Y = C.astype(float), R.astype(float)
        self.strength = mag / peak
        self.color = color
        self.arrow_width = arrow_width

    @classmethod
    def over(cls, panel, gx, gy, **kwargs):
        """A field aligned with ``panel`` (an ImagePanel of the same image)."""
        return cls(gx, gy, tuple(panel.rect), **kwargs)

    def own_bbox(self):
        x, y, w, h = self.rect
        return (x, y, x + w, y + h)

    def _shift_self(self, v):
        self.rect = self.rect + np.array([v[0], v[1], 0, 0])

    def draw(self, ctx, alpha, progress):
        H, W = self.image_shape
        ax = ctx.new_axes(tuple(self.rect))
        ax.set_xlim(-0.5, W - 0.5)
        ax.set_ylim(H - 0.5, -0.5)          # rows grow downward, like imshow
        ax.set_aspect("equal")
        ax.axis("off")
        ax.patch.set_alpha(0)
        show = (self.U != 0) | (self.V != 0)
        if self.color == "magnitude":
            colors = colormaps["plasma"](0.25 + 0.75 * self.strength[show])
        else:
            colors = self.color
        ax.quiver(self.X[show], self.Y[show], self.U[show] * progress, self.V[show] * progress,
                  color=colors, angles="xy", scale_units="xy", scale=1, width=self.arrow_width,
                  headwidth=3.5, headlength=4, alpha=alpha, zorder=3)
        ctx.ax = ctx.canvas


class GradientDiagram(Mobject):
    """The gradient at one pixel as a right triangle: Gx, then Gy, then the
    gradient vector, with a color-keyed readout of the numbers below.

    Drawn with image conventions (positive Gy points *down*), so it matches
    arrows drawn over images.

    Parameters
    ----------
    gx, gy : float
        Gradient components at the pixel.
    center : (x, y)
        Canvas position of the triangle area's center (the readout hangs
        below it).
    size : float
        Width/height of the square the triangle fits in (inches).
    scale : float, optional
        Inches per gradient unit; fix it to compare several gradients.
    show_angle : bool
        Draw the angle arc and include theta in the readout.
    decimals : int
        Digits shown for Gx and Gy.

    Notes
    -----
    The numbers sit in a readout rather than on the arrows, so they stay
    legible when the triangle is thin. ``Transform`` between two diagrams
    rotates and stretches the triangle while the numbers update.
    """

    def __init__(self, gx, gy, center=None, size=2.6, scale=None, show_angle=True, decimals=0,
                 label_size=15, **kwargs):
        super().__init__(**kwargs)
        th = DEFAULT_THEME
        self.gx, self.gy = float(gx), float(gy)
        self.center = np.array(center if center is not None else (th.width / 2, th.height / 2),
                               float)
        self.size = size
        biggest = max(abs(self.gx), abs(self.gy)) or 1.0
        self.scale = scale if scale is not None else 0.85 * size / biggest
        self.show_angle = show_angle
        self.decimals = decimals
        self.label_size = label_size

    def _line_h(self):
        return self.label_size / 72 * 1.6

    def own_bbox(self):
        h = self.size / 2
        cx, cy = self.center
        n = 4 if self.show_angle else 3
        return (cx - h, cy - h - 0.3 - n * self._line_h(), cx + h, cy + h)

    def _shift_self(self, v):
        self.center = self.center + v

    def _points(self):
        s = self.scale
        corner = np.array([self.gx * s, 0.0])
        tip = np.array([self.gx * s, -self.gy * s])
        lo = np.minimum.reduce([np.zeros(2), corner, tip])
        hi = np.maximum.reduce([np.zeros(2), corner, tip])
        o = self.center - (lo + hi) / 2          # center the triangle in its square
        return o, o + corner, o + tip

    def _fmt(self, v, d=None):
        d = self.decimals if d is None else d
        return f"{v:.{d}f}".replace("-", "\u2212")

    def draw(self, ctx, alpha, progress):
        ax = ctx.ax
        o, corner, tip = self._points()

        def arrow(a, b, color, lw, name):
            if np.linalg.norm(b - a) < 1e-3:
                return
            ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle="-|>", mutation_scale=16,
                                         color=color, lw=lw, alpha=alpha, shrinkA=0, shrinkB=0,
                                         zorder=3))
            ctx.register_segments(np.array([a, b]), name)

        # components grow first, then the resultant
        p1, p2, p3 = (float(np.clip(progress * 3 - k, 0, 1)) for k in range(3))
        arrow(o, o + (corner - o) * p1, ORANGE, 2.5, "Gx")
        if p2 > 0:
            arrow(corner, corner + (tip - corner) * p2, PURPLE, 2.5, "Gy")
        if p3 > 0:
            arrow(o, o + (tip - o) * p3, ACCENT, 3.5, "gradient")
        ax.plot(*o, "o", ms=7, color=TEXT, alpha=alpha, zorder=4)
        if progress < 1:
            return

        ang = np.degrees(np.arctan2(self.gy, self.gx))
        if self.show_angle and np.hypot(self.gx, self.gy) > 1e-9:
            screen = -ang
            r = min(0.5, 0.45 * np.linalg.norm(tip - o))
            th1, th2 = sorted([0.0, screen])
            ax.add_patch(Arc(tuple(o), 2 * r, 2 * r, theta1=th1, theta2=th2, color=SUB, lw=1.5,
                             alpha=alpha))
        rows = [(rf"$G_x = {self._fmt(self.gx)}$", ORANGE),
                (rf"$G_y = {self._fmt(self.gy)}$", PURPLE),
                (rf"$|\nabla I| = {self._fmt(np.hypot(self.gx, self.gy), max(self.decimals, 1))}$",
                 ACCENT)]
        if self.show_angle:
            rows.append((rf"$\theta = {ang:.0f}^\circ$", SUB))
        x = self.center[0] - self.size / 2 + 0.15
        y = self.center[1] - self.size / 2 - 0.3
        for i, (txt, color) in enumerate(rows):
            ax.text(x, y - i * self._line_h(), txt, fontsize=self.label_size, color=color,
                    weight="bold", ha="left", va="top", alpha=alpha)


class EdgeProfile(Mobject):
    """One row of pixels plotted as a signal, with its derivatives below.

    Shows why edges are found where the first derivative peaks and the second
    derivative crosses zero.

    Parameters
    ----------
    signal : 1-D array
        Intensities along a row (see ``pixelmotion.data.edge_signal``).
    rect : Region or (x, y, w, h)
        Canvas area for the stacked plots.
    show : tuple of str
        Which rows to draw, top to bottom, from "image" (the pixels
        themselves, lined up with the plots), "intensity", "first", "second".
    mark : bool
        Mark the edge: the first-derivative peak and second-derivative zero
        crossing, joined by a dashed line through every plot.

    Notes
    -----
    ``Create`` sweeps the plots left to right. ``Transform`` to a profile of
    another signal (e.g. a step becoming a ramp) morphs every curve.
    """

    TITLES = {"image": "", "intensity": "Intensity", "first": "1st derivative (change)",
              "second": "2nd derivative (change of change)"}
    COLORS = {"image": TEXT, "intensity": TEXT, "first": ACCENT, "second": PURPLE}

    def __init__(self, signal, rect, show=("intensity", "first"), mark=True, x_label="pixel",
                 **kwargs):
        super().__init__(**kwargs)
        self.signal = np.asarray(signal, float)
        self.rect = np.array(getattr(rect, "rect", rect), float)
        self.show = tuple(show)
        self.mark = mark
        self.x_label = x_label

    def curves(self):
        s = self.signal
        first = np.gradient(s)
        second = np.gradient(first)
        return {"intensity": s, "first": first, "second": second}

    def edge_position(self):
        """Where the edge is, in pixels: the middle of the first derivative's
        peak (sub-pixel, e.g. 15.5 for an edge between pixels 15 and 16)."""
        d = np.abs(self.curves()["first"])
        return float(np.mean(np.flatnonzero(d >= 0.98 * d.max())))

    def zero_crossing(self):
        """Where the second derivative changes sign nearest the edge."""
        c, e = self.curves()["second"], self.edge_position()
        best = None
        for i in range(len(c) - 1):
            # a real sign change (flat runs of zeros are not crossings)
            if c[i] * c[i + 1] < 0:
                x = i + c[i] / (c[i] - c[i + 1])
                if best is None or abs(x - e) < abs(best - e):
                    best = x
        return e if best is None else best

    def own_bbox(self):
        x, y, w, h = self.rect
        return (x, y, x + w, y + h)

    def _shift_self(self, v):
        self.rect = self.rect + np.array([v[0], v[1], 0, 0])

    def draw(self, ctx, alpha, progress):
        x, y, w, h = self.rect
        k = len(self.show)
        gap, left, bottom = 0.45, 0.9, 0.45
        weights = [0.45 if key == "image" else 1.0 for key in self.show]
        unit = (h - bottom - gap * (k - 1)) / sum(weights)
        curves = self.curves()
        n = len(self.signal)
        xs = np.arange(n)
        upto = max(1, int(np.ceil(progress * n)))
        edge = self.edge_position()
        top = y + h
        for i, key in enumerate(self.show):
            ph = weights[i] * unit
            top -= ph
            ax = ctx.new_axes((x + left, top, w - left, ph))
            top -= gap
            ax.set_xlim(-0.5, n - 0.5)
            ax.patch.set_alpha(0)
            if key == "image":
                ax.imshow(self.signal[None, :], cmap="gray", vmin=0, vmax=255, aspect="auto",
                          extent=(-0.5, n - 0.5, 0, 1), alpha=alpha, interpolation="nearest")
                ax.set_axis_off()
                if self.mark and progress >= 1:
                    ax.axvline(edge, color=ACCENT2, ls="--", lw=1.4, alpha=0.8 * alpha)
                continue
            c = curves[key]
            span = np.ptp(c) or 1.0
            ax.set_ylim(c.min() - 0.15 * span, c.max() + 0.3 * span)
            ax.set_autoscale_on(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_color(SUB)
                ax.spines[side].set_alpha(alpha)
            ax.tick_params(colors=SUB, labelsize=9)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=3))
            if i < k - 1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel(self.x_label, fontsize=11, color=SUB, alpha=alpha)
            if key != "intensity":
                ax.axhline(0, color=SUB, lw=0.8, alpha=0.6 * alpha)
            ax.plot(xs[:upto], c[:upto], color=self.COLORS[key], lw=2.4, alpha=alpha,
                    drawstyle="steps-mid" if key == "intensity" else "default")
            ctx.ax = ax
            ctx.register_segments(np.c_[xs[:upto], c[:upto]], self.TITLES[key])
            ax.text(0.01, 0.97, self.TITLES[key], transform=ax.transAxes, fontsize=12,
                    color=self.COLORS[key], weight="bold", ha="left", va="top", alpha=alpha)
            if self.mark and progress >= 1:
                ax.axvline(edge, color=ACCENT2, ls="--", lw=1.4, alpha=0.8 * alpha)
                if key == "first":
                    peak = np.interp(edge, xs, c)
                    ax.plot(edge, peak, "o", ms=9, color=ACCENT2, alpha=alpha, zorder=4)
                    # above the peak: nothing on the curve is higher
                    ax.text(edge + 0.6, peak + 0.06 * span, "peak = edge", fontsize=12,
                            color=ACCENT2, weight="bold", ha="left", va="bottom", alpha=alpha)
                if key == "second":
                    zc = self.zero_crossing()
                    ax.plot(zc, 0, "o", ms=9, color=GREEN, alpha=alpha, zorder=4)
                    # right of the crossing, above the axis: the curve dips below there
                    ax.text(zc + 1.2, 0.08 * span, "zero crossing = edge", fontsize=12,
                            color=GREEN, weight="bold", ha="left", va="bottom", alpha=alpha)
        ctx.ax = ctx.canvas
