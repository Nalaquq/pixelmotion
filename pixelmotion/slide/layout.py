"""Slide regions, the info panel, and the Slide scene with built-in chrome."""

import re
import warnings
from dataclasses import dataclass

import numpy as np

from ..basics.shapes import RoundedBox
from ..basics.text import Text, measure
from ..core.mobject import Group
from ..core.scene import Scene
from ..theme import ACCENT, PANEL_BG, SUB, TEXT


@dataclass
class Region:
    """A rectangle of the canvas: ``x, y`` bottom-left, ``w, h`` size (inches)."""

    x: float
    y: float
    w: float
    h: float

    @property
    def rect(self):
        return (self.x, self.y, self.w, self.h)

    @property
    def center(self):
        return np.array([self.x + self.w / 2, self.y + self.h / 2])

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.h

    def inset(self, pad):
        return Region(self.x + pad, self.y + pad, self.w - 2 * pad, self.h - 2 * pad)

    def split(self, n, axis="x", gap=0.3):
        """``n`` equal sub-regions side by side (``axis="x"``) or stacked."""
        if axis == "x":
            w = (self.w - gap * (n - 1)) / n
            return [Region(self.x + i * (w + gap), self.y, w, self.h) for i in range(n)]
        h = (self.h - gap * (n - 1)) / n
        return [Region(self.x, self.top - (i + 1) * h - i * gap, self.w, h) for i in range(n)]


def Title(text, subtitle=None, theme=None):
    """Bold slide title with an optional italic subtitle, at style-guide positions."""
    from ..theme import DEFAULT_THEME
    th = theme or DEFAULT_THEME
    parts = [Text(text, pos=(th.width / 2, 0.95 * th.height), size=th.title_size,
                  weight="bold", va="baseline", name="title")]
    if subtitle:
        parts.append(Text(subtitle, pos=(th.width / 2, 0.895 * th.height),
                          size=th.subtitle_size, color=SUB, style="italic",
                          va="baseline", name="subtitle"))
    return Group(*parts, name="title")


_TOKEN = re.compile(r"\$[^$]*\$|\S+")


def wrap(text, width, size, weight="normal"):
    """Greedy word-wrap to ``width`` inches; never splits inside ``$...$``."""
    words = _TOKEN.findall(text)
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if cur and measure(cand, size, weight)[0] > width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines or [""]


class InfoPanel(Group):
    """The rounded left-hand explanation box, laid out and wrapped for you.

    Items (one per list entry):

    * ``"# Heading"`` - accent-colored bold heading
    * ``"plain text"`` - body text, wrapped to the panel width
    * ``"~ aside"`` - subdued gray text
    * ``("E(h) = 170 cm", GREEN)`` - bold text in a color
    * ``""`` - a blank gap

    ``panel.items[i]`` is the i-th entry (a Group of its wrapped lines), so
    you can reveal them one by one with ``LaggedStart(*[FadeIn(i) for i in
    panel.items])``.
    """

    def __init__(self, items, region, pad=0.3, line_spacing=1.45, heading_size=None,
                 body_size=None, align="center", **kwargs):
        from ..theme import DEFAULT_THEME
        th = DEFAULT_THEME
        hs = heading_size or th.heading_size
        bs = body_size or th.body_size
        box = RoundedBox(region.w, region.h, region.center, corner_radius=0.2,
                         color=ACCENT, fill=PANEL_BG, stroke=2, name="panel_box")
        super().__init__(box, **kwargs)
        inner = region.inset(pad)
        x = {"center": inner.center[0], "left": inner.left}[align]
        y = inner.top
        for k, item in enumerate(items):
            if item == "":
                y -= bs / 72 * line_spacing * 0.7
                self.add(Group(name="gap"))
                continue
            if isinstance(item, tuple):
                text, color = item
                style = dict(size=bs + 1, color=color, weight="bold")
            elif item.startswith("# "):
                text = item[2:]
                style = dict(size=hs, color=ACCENT, weight="bold")
                if k > 0:
                    y -= bs / 72 * 0.5
            elif item.startswith("~ "):
                text = item[2:]
                style = dict(size=bs, color=SUB)
            else:
                text = item
                style = dict(size=bs, color=TEXT)
            lines = wrap(text, inner.w, style["size"], style.get("weight", "normal"))
            group = Group(name=text[:24])
            for line in lines:
                group.add(Text(line, pos=(x, y), ha=align, va="top", **style))
                y -= style["size"] / 72 * line_spacing
            self.add(group)
        if y < inner.bottom:
            warnings.warn(f"InfoPanel content overflows its box by {inner.bottom - y:.2f} in; "
                          "shorten the text or reduce body_size.", stacklevel=2)

    @property
    def box(self):
        return self.submobjects[0]

    @property
    def items(self):
        return self.submobjects[1:]


class Slide(Scene):
    """A Scene with the course slide layout already in place.

    Set class attributes and use the regions to place content::

        class MeanCentering(Slide):
            title = "Step 1: Mean-Centering the Data"
            subtitle = "Subtract each column's mean"
            info = ["# Why centre?", "PCA finds directions of maximum variance."]

            def construct(self):
                X = Matrix(...).move_to(self.main)

    Regions (canvas units, 16 x 9): ``self.full``, ``self.left`` (info
    panel), ``self.right``, and ``self.main`` (= ``right`` when there is an
    info panel, else the full content width). Content sits below the title.
    """

    title = ""
    subtitle = ""
    info = None

    def setup(self):
        th = self.theme
        W, H = th.width, th.height
        content_top = 0.86 * H
        bottom = 0.04 * H
        self.full = Region(0, 0, W, H)
        self.content = Region(0.02 * W, bottom, 0.96 * W, content_top - bottom)
        self.left = Region(0.02 * W, bottom, 0.30 * W, 0.78 * H)
        self.right = Region(0.34 * W, bottom, 0.64 * W, content_top - bottom)
        self.main = self.right if self.info is not None else self.content
        self.info_panel = None
        if self.title:
            self.add(Title(self.title, self.subtitle, th))
        if self.info is not None:
            self.info_panel = InfoPanel(self.info, self.left)
            self.add(self.info_panel)
