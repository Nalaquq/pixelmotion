# Positioning

The canvas is **16 × 9 units (inches)** with `(0, 0)` at the bottom-left.
Direction constants: `UP`, `DOWN`, `LEFT`, `RIGHT`, `UL`, `UR`, `DL`, `DR`.

| Method | Example |
|---|---|
| `move_to(point / mobject / region)` | `m.move_to(self.main)` |
| `move_to(..., aligned_edge=LEFT)` | line up left edges |
| `next_to(other, direction, buff)` | `label.next_to(grid, DOWN, buff=0.3)` |
| `shift(vector)` | `m.shift(UP * 0.5 + RIGHT)` |
| `Group(...).arrange(direction, buff)` | `Group(a, b, c).arrange(RIGHT, buff=0.5)` |
| `get_center()`, `get_top()`, `get_edge(DR)` | anchor points |

## Regions

In a `Slide`, `self.main`, `self.left`, `self.right`, `self.content` and
`self.full` are `Region`s. Split them for side-by-side layouts:

```python
left, mid, right = self.main.split(3, gap=0.2)          # three columns
top, bottom = self.main.split(2, axis="y")              # two rows
image = PixelGrid(img).move_to(left)
```

## Inside a plane

Objects added to a `Plane` use the plane's own coordinates. Use
`plane.c2p(x, y)` to get the canvas point for a plane point.

::: pixelmotion.core.Mobject
    options:
      members: [move_to, next_to, shift, get_center, get_edge, bbox, set_color,
                set_opacity, add_updater, copy, become]
