# Writing new objects

A mobject is a class with attributes and a `draw` method. Animations work
automatically because they only change attributes.

```python
import numpy as np
from pixelmotion import Mobject, ACCENT

class BoundingBox(Mobject):
    """A detection box with a class label and confidence."""

    def __init__(self, x0, y0, x1, y1, label="", score=1.0, color=ACCENT, **kwargs):
        super().__init__(**kwargs)
        self.corners = np.array([x0, y0, x1, y1], float)
        self.label, self.score, self.color = label, score, color

    def own_bbox(self):
        return tuple(self.corners)

    def _shift_self(self, v):
        self.corners = self.corners + np.r_[v, v]

    def draw(self, ctx, alpha, progress):
        x0, y0, x1, y1 = self.corners
        ctx.ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0],
                    color=self.color, lw=2.5, alpha=alpha)
        ctx.ax.text(x0, y1 + 0.1, f"{self.label} {self.score:.2f}", color=self.color,
                    fontsize=12, weight="bold", alpha=alpha, va="bottom")
```

Now `Transform(box, box2)` slides and resizes it, interpolates the score,
and blends the color.

## Rules of thumb

1. **Store state as numbers, arrays, and colors.** These interpolate. Put
   colors in attributes whose name contains `color`.
2. **Draw in `draw(ctx, alpha, progress)`.** Multiply every artist's alpha by
   `alpha`; use `progress` (0 to 1) for `Create`.
3. **Children go in `self.submobjects`** (via `self.add`). Expose them with
   properties, not extra attributes, so copies stay consistent.
4. **Implement `own_bbox` and `_shift_self`** so positioning works.
5. **Need your own axes** (images, 3D, data plots)? Use
   `ax = ctx.new_axes((x, y, w, h))`. See `ImagePanel` for an example.
6. **Large arrays you never mutate** (photos) go in `_no_copy` so frame
   snapshots share them.
7. **Call `ctx.register_segments(points)`** for lines that labels must not
   cover.
