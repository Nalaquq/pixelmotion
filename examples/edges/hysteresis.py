"""Hysteresis: strong edges recruit the weak pixels they touch."""

import numpy as np

from pixelmotion import *


class HysteresisSlide(Slide):
    title = "Canny Step 5: Edge Tracking by Hysteresis"
    subtitle = "Weak pixels survive only if they connect to a strong edge"
    info = [
        "# Two thresholds",
        ("S (white): certainly an edge", TEXT),
        ("W (orange): maybe an edge", ORANGE),
        "",
        "# Grow",
        "Each step, weak pixels touching a strong one become strong.",
        "",
        "# Clean up",
        "Weak pixels that never connected are noise: drop them.",
    ]

    def construct(self):
        L = np.zeros((8, 10), int)
        L[1, 1:3] = 2                      # a strong seed...
        L[1, 3:6] = 1                      # ...with a weak tail to recruit
        L[2, 6] = 1
        L[3, 7] = 1
        L[4, 7] = 2                        # joins a second strong piece
        L[5, 7:9] = 1
        L[6, 2] = 1                        # isolated weak specks
        L[5, 4] = 1
        grid = PixelGrid(L, cell=0.6, cmap="labels", vmin=0, vmax=2,
                         value_labels={0: "", 1: "W", 2: "S"}, label="Thresholded pixels")
        grid.move_to(self.main)
        self.play(Create(grid), run_time=2)
        self.wait()
        self.play(Hysteresis(grid, time_per_wave=1.2))
        self.wait(2)


if __name__ == "__main__":
    HysteresisSlide().render_gif("out/hysteresis.gif")
