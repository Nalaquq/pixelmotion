"""Text and math labels."""

from functools import lru_cache

import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath
from matplotlib.transforms import Bbox, TransformedBbox

from ..core.mobject import Mobject
from ..theme import DEFAULT_THEME, TEXT

_t2p = TextToPath()


@lru_cache(maxsize=4096)
def measure(text, size, weight="normal", style="normal", family=None, linespacing=1.2):
    """(width, height, descent) of ``text`` in canvas units (inches)."""
    prop = FontProperties(size=size, weight=weight, style=style,
                          family=family or DEFAULT_THEME.font_family)
    lines = text.split("\n")
    widths, heights, descent = [], [], 0.0
    for line in lines:
        ismath = line.count("$") >= 2 and line.count("$") % 2 == 0
        w, h, d = _t2p.get_text_width_height_descent(line or " ", prop, ismath=ismath)
        widths.append(w)
        heights.append(h)
        descent = d
    height = sum(heights) + (len(lines) - 1) * size * (linespacing - 1)
    return max(widths) / 72, height / 72, descent / 72


class Text(Mobject):
    """A text label; ``$...$`` segments render as math (matplotlib mathtext).

    Parameters
    ----------
    text : str
        The string. Use ``r"$x_1$"`` for subscripts; avoid Unicode subscripts.
    pos : (x, y), optional
        Anchor point, in canvas units (default: canvas center).
    size : float
        Font size in points (default: ``theme.body_size``).
    ha, va : str
        Which part of the text sits on ``pos`` ("left"/"center"/"right",
        "top"/"center"/"bottom"/"baseline").

    Notes
    -----
    ``Create``/``Write`` reveal it left to right.
    """

    def __init__(self, text, pos=None, size=None, color=TEXT, weight="normal",
                 style="normal", ha="center", va="center", family=None,
                 rotation=0.0, **kwargs):
        super().__init__(**kwargs)
        self.text = str(text)
        th = DEFAULT_THEME
        self.pos = np.array(pos if pos is not None else (th.width / 2, th.height / 2), float)
        self.size = th.body_size if size is None else size
        self.color = color
        self.weight = weight
        self.style = style
        self.ha = ha
        self.va = va
        self.family = family
        self.rotation = rotation

    def _measure(self):
        return measure(self.text, self.size, self.weight, self.style, self.family)

    def own_bbox(self):
        w, h, d = self._measure()
        x0 = {"left": 0.0, "center": -w / 2, "right": -w}[self.ha] + self.pos[0]
        y0 = {"bottom": 0.0, "baseline": -d, "center": -h / 2, "center_baseline": -h / 2,
              "top": -h}[self.va] + self.pos[1]
        return (x0, y0, x0 + w, y0 + h)

    def _shift_self(self, v):
        self.pos = self.pos + v

    def set_text(self, text):
        self.text = str(text)
        return self

    def draw(self, ctx, alpha, progress):
        x, y = ctx.tf(self.pos[None, :])[0]
        on_canvas = ctx.on_canvas
        art = ctx.ax.text(
            x, y, self.text, fontsize=self.size, color=self.color,
            fontweight=self.weight, fontstyle=self.style, ha=self.ha, va=self.va,
            family=self.family or ctx.theme.font_family, rotation=self.rotation,
            alpha=alpha if (progress >= 1 or on_canvas) else alpha * progress,
            zorder=3 + self.z)
        if progress < 1 and on_canvas:
            x0, y0, x1, y1 = self.own_bbox()
            pad = self.size / 72
            clip = Bbox([[x0 - pad, y0 - pad], [x0 + (x1 - x0) * progress, y1 + pad]])
            art.set_clip_box(TransformedBbox(clip, ctx.ax.transData))
            art.set_clip_on(True)
        return art

