"""Bracketed matrices whose entries can morph, highlight, and be labeled."""

import numpy as np
from matplotlib.patches import FancyBboxPatch

from ..basics.text import Text, measure
from ..core.mobject import Mobject
from ..theme import ACCENT, DEFAULT_THEME, ORANGE, SUB, TEXT

MINUS = "−"


class Matrix(Mobject):
    """A matrix in square brackets.

    Parameters
    ----------
    entries : 2-D list or array
        Numbers (which interpolate smoothly under ``Transform``) or strings
        (e.g. ``r"$h_1$"``; these cross-fade).
    center : (x, y)
        Canvas position of the matrix center (default: canvas center).
    size : float
        Font size of entries in points.
    colors : color, list of colors (one per row), or 2-D list
    decimals : int, optional
        Digits after the point; default 0 if every value is a whole number.
    signed : bool
        Prefix positive numbers with "+".
    label : str, optional
        Name drawn above, e.g. ``r"$X$"``.
    col_labels, row_labels : list of str, optional

    Example
    -------
    >>> X = Matrix([[150, 50], [170, 70], [190, 60]], label=r"$X$",
    ...            col_labels=["height", "weight"])
    >>> centered = X.copy().set_values(X.values - X.values.mean(axis=0))
    >>> self.play(Transform(X, centered))      # numbers count to new values
    """

    def __init__(self, entries, center=None, size=20, colors=TEXT, decimals=None,
                 signed=False, row_gap=None, col_gap=None, bracket_color=TEXT, label=None,
                 label_color=ACCENT, col_labels=None, row_labels=None,
                 family="monospace", **kwargs):
        super().__init__(**kwargs)
        arr = np.array(entries, dtype=object)
        if arr.ndim == 1:
            arr = arr[None, :]
        self.shape = arr.shape
        numeric = all(isinstance(v, (int, float, np.integer, np.floating)) for v in arr.flat)
        self.values = arr.astype(float) if numeric else None
        self.strings = None if numeric else [[str(v) for v in row] for row in arr]
        if decimals is None and numeric:
            decimals = 0 if np.allclose(self.values, np.round(self.values)) else 2
        self.decimals = decimals or 0
        self.signed = signed
        self.size = size
        self.family = family
        nr, nc = self.shape
        if isinstance(colors, str):
            self.entry_colors = [[colors] * nc for _ in range(nr)]
        elif all(isinstance(c, str) for c in colors):
            self.entry_colors = [[colors[i % len(colors)]] * nc for i in range(nr)]
        else:
            self.entry_colors = [list(r) for r in colors]
        self.bracket_color = bracket_color
        self.row_band = np.zeros(nr)
        self.col_band = np.zeros(nc)
        self.band_color = ORANGE
        u = size / 72
        self.row_gap = row_gap if row_gap is not None else 2.0 * u
        widest = max(measure(s, size, family=family)[0] for s in self._all_strings())
        self.col_gap = col_gap if col_gap is not None else widest + 1.2 * u
        self.entry_w = widest
        th = DEFAULT_THEME
        self.center = np.array(center if center is not None else (th.width / 2, th.height / 2),
                               float)
        self._add_labels(label, label_color, col_labels, row_labels)

    def _add_labels(self, label, label_color, col_labels, row_labels):
        """Labels are child Text mobjects, so changing one cross-fades only
        that label while the entries keep interpolating."""
        u = self.size / 72
        hw, hh = self._bracket_extent()
        cx, cy = self.center
        top = cy + hh
        for j, s in enumerate(col_labels or []):
            self.add(Text(s, pos=(self.entry_pos(0, j)[0], top + 0.5 * u), size=self.size * 0.6,
                          color=SUB, style="italic", name=f"col_label_{j}"))
        if col_labels:
            top += 1.1 * u
        if label:
            self.add(Text(label, pos=(cx, top + 0.7 * u), size=self.size * 0.95,
                          color=label_color, weight="bold", name="label"))
        for i, s in enumerate(row_labels or []):
            self.add(Text(s, pos=(cx - hw - 0.4 * u, self.entry_pos(i, 0)[1]),
                          size=self.size * 0.6, color=self.entry_colors[i][0], style="italic",
                          weight="bold", ha="right", name=f"row_label_{i}"))

    def get_label(self):
        """The name label above the matrix (a Text), or None."""
        return next((m for m in self.submobjects if m.name == "label"), None)

    def set_label(self, text):
        lab = self.get_label()
        if lab is not None:
            lab.set_text(text)
        return self

    # ── Values ─────────────────────────────────────────────────────────
    def format(self, v):
        s = f"{v:.{self.decimals}f}"
        if self.decimals == 0:
            s = f"{int(np.round(v))}"
        if s.lstrip("-").strip("0.") == "":
            s = s.lstrip("-")   # no "-0"
        if self.signed and not s.startswith("-") and s.strip("0.") != "":
            s = "+" + s
        return s.replace("-", MINUS)

    def _all_strings(self):
        if self.values is None:
            return [s for row in self.strings for s in row]
        return [self.format(v) for v in self.values.flat]

    def entry_text(self, i, j):
        return self.strings[i][j] if self.values is None else self.format(self.values[i, j])

    def set_values(self, values):
        """Replace numeric entries (same shape). Returns self."""
        self.values = np.array(values, float).reshape(self.shape)
        self.strings = None
        return self

    def set_entries(self, entries):
        """Replace entries with strings (e.g. symbols). Returns self."""
        self.strings = [[str(v) for v in row] for row in entries]
        self.values = None
        return self

    def set_color(self, color):
        nr, nc = self.shape
        self.entry_colors = [[color] * nc for _ in range(nr)]
        return self

    def set_row_colors(self, colors):
        nr, nc = self.shape
        self.entry_colors = [[colors[i % len(colors)]] * nc for i in range(nr)]
        return self

    def highlight_row(self, i, strength=1.0):
        self.row_band = self.row_band.copy()
        self.row_band[i] = strength
        return self

    def highlight_col(self, j, strength=1.0, color=ORANGE):
        self.col_band = self.col_band.copy()
        self.col_band[j] = strength
        self.band_color = color
        return self

    def unhighlight(self):
        self.row_band = np.zeros_like(self.row_band)
        self.col_band = np.zeros_like(self.col_band)
        return self

    # ── Geometry ───────────────────────────────────────────────────────
    def entry_pos(self, i, j):
        nr, nc = self.shape
        return self.center + np.array([(j - (nc - 1) / 2) * self.col_gap,
                                       ((nr - 1) / 2 - i) * self.row_gap])

    def row_pos(self, i):
        return np.array([self.center[0], self.entry_pos(i, 0)[1]])

    def _bracket_extent(self):
        nr, nc = self.shape
        u = self.size / 72
        hw = (nc - 1) * self.col_gap / 2 + self.entry_w / 2 + 0.45 * u
        hh = (nr - 1) * self.row_gap / 2 + 0.9 * u
        return hw, hh

    def own_bbox(self):
        hw, hh = self._bracket_extent()
        cx, cy = self.center
        return (cx - hw, cy - hh, cx + hw, cy + hh)

    def _shift_self(self, v):
        self.center = self.center + v

    # ── Drawing ────────────────────────────────────────────────────────
    def draw(self, ctx, alpha, progress):
        ax, nr, nc = ctx.ax, *self.shape
        u = self.size / 72
        hw, hh = self._bracket_extent()
        cx, cy = self.center
        arm = 0.35 * u
        for side in (-1, 1):
            x = cx + side * hw
            ax.plot([x - side * arm, x, x, x - side * arm], [cy + hh, cy + hh, cy - hh, cy - hh],
                    color=self.bracket_color, lw=2.5, alpha=alpha, solid_capstyle="butt")
        for i in range(nr):
            if self.row_band[i] > 0.01:
                y = self.entry_pos(i, 0)[1]
                ax.add_patch(FancyBboxPatch(
                    (cx - hw + 0.15 * u, y - 0.55 * u), 2 * hw - 0.3 * u, 1.1 * u,
                    boxstyle=f"round,pad={0.1 * u}", facecolor=self.entry_colors[i][0],
                    edgecolor="none", alpha=0.18 * self.row_band[i] * alpha, zorder=0))
        for j in range(nc):
            if self.col_band[j] > 0.01:
                x = self.entry_pos(0, j)[0]
                ax.add_patch(FancyBboxPatch(
                    (x - self.col_gap / 2 + 0.2 * u, cy - hh + 0.2 * u), self.col_gap - 0.4 * u,
                    2 * hh - 0.4 * u, boxstyle=f"round,pad={0.05 * u}",
                    facecolor=self.band_color, edgecolor="none",
                    alpha=0.18 * self.col_band[j] * alpha, zorder=0))
        shown = int(np.ceil(progress * nr * nc - 1e-9))
        for k in range(min(shown, nr * nc)):
            i, j = divmod(k, nc)
            x, y = self.entry_pos(i, j)
            ax.text(x, y, self.entry_text(i, j), fontsize=self.size, color=self.entry_colors[i][j],
                    weight="bold", ha="center", va="center", family=self.family, alpha=alpha,
                    zorder=3)
