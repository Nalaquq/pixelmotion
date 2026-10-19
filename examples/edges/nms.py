"""Non-maximum suppression: thin a thick ridge of gradient to a one-pixel edge."""

import numpy as np

from pixelmotion import *
from pixelmotion import edges


class NMSSlide(Slide):
    title = "Canny Step 3: Non-Maximum Suppression"
    subtitle = "Keep a pixel only if it beats its two neighbours along the gradient"
    info = [
        "# Why?",
        "Gradients are thick: several pixels respond to one edge.",
        "",
        "# The test",
        "Look along the gradient direction.",
        ("Biggest of the three: keep", GREEN),
        ("Otherwise: suppress to 0", RED),
        "",
        "~ The result is an edge one pixel wide.",
    ]

    def construct(self):
        x = np.arange(7)
        ridge = np.exp(-((x - 3.2) ** 2) / 2.0)          # a soft vertical edge response
        mag = np.round(np.tile(ridge, (6, 1)) * 90 + np.array([[0, 3, 1, 4, 0, 2, 1]]))
        gx, gy = np.ones_like(mag), np.zeros_like(mag)     # gradient points right everywhere
        angle = edges.gradient_direction(gx, gy)

        left, right = self.main.split(2, gap=0.6)
        grid = PixelGrid(mag, center=left.center, cell=0.55, cmap="magma", vmin=0, vmax=100,
                         label="Gradient magnitude")
        out = PixelGrid.empty(mag.shape, center=right.center, cell=0.55, cmap="magma", vmin=0,
                              vmax=100, label="After NMS")
        self.play(FadeIn(grid), FadeIn(out))
        self.play(NonMaxSuppression(grid, angle, out, cells=[(1, 2), (1, 3), (1, 4)],
                                    time_per_cell=2.0))
        rest = [(r, c) for r in range(1, 5) for c in range(1, 6)
                if (r, c) not in [(1, 2), (1, 3), (1, 4)]]
        self.play(NonMaxSuppression(grid, angle, out, cells=rest, time_per_cell=0.4))
        self.wait(2)


if __name__ == "__main__":
    NMSSlide().render_gif("out/nms.gif")
