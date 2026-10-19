# Getting started

## Install

```bash
pip install git+https://github.com/Nalaquq/pixelmotion
```

pixelmotion needs Python 3.10+, NumPy, matplotlib, and Pillow. No LaTeX,
Cairo, or ffmpeg: math is rendered with matplotlib's built-in mathtext.

## Your first scene

A **scene** is a class with a `construct` method. Inside it you create
objects and `play` animations on them, exactly like manim:

```python
from pixelmotion import *

class Hello(Scene):
    def construct(self):
        title = Text("Hello, pixels", size=40, weight="bold")
        self.play(Write(title))
        self.play(title.animate.shift(UP * 2).set_color(ACCENT))
        self.wait()

Hello().render_gif("hello.gif")
```

`render_gif` writes a GIF using the slide defaults: 500 ms per animation
frame, plays once, and holds the last frame for 60 s so it sits still on a
slide. Use `render_png()` for a still of the last frame.

!!! tip "Fast drafts"
    `render_gif("draft.gif", dpi=50)` renders at a third of the resolution,
    which is much faster while you iterate.

## Your first slide

`Slide` is a scene with the course layout built in: a title, an optional
info panel on the left, and named regions to place content in.

```python
class Pixels(Slide):
    title = "An Image Is a Grid of Numbers"
    subtitle = "Each cell stores a brightness from 0 (black) to 255 (white)"
    info = ["# Grayscale", "One number per pixel.", "", "~ Colour images store three."]

    def construct(self):
        grid = PixelGrid([[0, 64, 128], [64, 128, 192], [128, 192, 255]],
                         cell=0.9).move_to(self.main)
        self.play(Create(grid))      # cells fill in reading order
        self.wait(2)
```

## Coordinates in one sentence

The canvas is **16 × 9 units, one unit = one inch**, with the origin at the
bottom-left, so `(8, 4.5)` is the center. Most of the time you won't type
coordinates at all: use `move_to(self.main)`, `next_to(other, RIGHT)`, and
`Group(...).arrange(DOWN)` (see [Positioning](guide/positioning.md)).
