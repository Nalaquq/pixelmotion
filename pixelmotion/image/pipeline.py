"""A row (or grid) of images joined by arrows: one panel per processing step."""

import numpy as np

from ..basics.shapes import Arrow
from ..core.mobject import Group
from ..theme import SUB
from .grids import ImagePanel

_KINDS = {"gray": {}, "signed": {"signed": True}, "labels": {"cmap": "labels"}}


class ImagePipeline(Group):
    """Images for each step of an algorithm, left to right, with arrows.

    Parameters
    ----------
    stages : list of tuples
        ``(title, image)`` or ``(title, image, kind)`` where ``kind`` is
        "gray" (default), "signed" (red/blue around zero), "labels" (0/1/2
        maps), or any colormap name.
    region : Region or (x, y, w, h)
        Area to fill.
    cols : int, optional
        Panels per row (default: all in one row up to 4, else two rows).
    gap : float
        Space between panels, in inches (arrows go in the gaps).

    Notes
    -----
    ``Create(pipeline)`` reveals the steps one after another. ``panels`` and
    ``arrows`` give the parts, e.g. to ``Indicate`` one step.
    """

    def __init__(self, stages, region, cols=None, gap=0.55, title_size=13, arrow_color=SUB,
                 **kwargs):
        super().__init__(**kwargs)
        x, y, w, h = getattr(region, "rect", region)
        n = len(stages)
        cols = cols or (n if n <= 4 else int(np.ceil(n / 2)))
        rows = int(np.ceil(n / cols))
        title_h = title_size / 72 * 2.2
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        prev = None
        for k, stage in enumerate(stages):
            title, image = stage[0], stage[1]
            kind = stage[2] if len(stage) > 2 else "gray"
            opts = _KINDS.get(kind, {"cmap": kind})
            r, c = divmod(k, cols)
            rect = (x + c * (cw + gap), y + h - (r + 1) * ch - r * gap, cw, ch - title_h)
            panel = ImagePanel(image, rect, title=title, title_size=title_size,
                               name=f"stage {k}", **opts)
            if prev is not None and prev[1] == r:
                a = prev[0].image_box()
                b = panel.image_box()
                ymid = (b[1] + b[3]) / 2
                arrow = Arrow((a[2] + 0.08, ymid), (b[0] - 0.08, ymid), color=arrow_color,
                              stroke=2.5, head=14, name=f"arrow {k}")
                arrow.check_labels = False
                self.add(arrow)
            self.add(panel)
            prev = (panel, r)

    @property
    def panels(self):
        return [m for m in self.submobjects if isinstance(m, ImagePanel)]

    @property
    def arrows(self):
        return [m for m in self.submobjects if isinstance(m, Arrow)]
