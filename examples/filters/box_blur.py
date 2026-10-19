"""Box blur as a sliding window: the kernel visits each pixel neighbourhood."""

import numpy as np

from pixelmotion import *


class BoxBlur(Slide):
    title = "Box Blur: A Sliding Window"
    subtitle = "Each output pixel is the average of the 3×3 neighbourhood under the kernel"
    info = [
        "# How it works",
        "Place the kernel on the image, multiply overlapping values, and add them up.",
        "",
        "# The box kernel",
        "Every weight is 1/9, so the sum is the neighbourhood's mean.",
        "",
        "~ Bright outliers get averaged away: that is the blur.",
    ]

    def construct(self):
        rng = np.random.default_rng(3)
        img = np.clip(rng.normal(120, 25, (6, 6)), 0, 255).round()
        img[2, 3] = 250   # a noisy bright pixel

        left, mid, right = self.main.split(3, gap=0.2)
        image = PixelGrid(img, center=left.center, cell=0.5, label="Input image")
        kernel = Kernel(np.ones((3, 3)), scale="1/9", center=mid.center, label="Kernel")
        output = PixelGrid.empty((4, 4), center=right.center, cell=0.5, fmt="{:.0f}",
                             label="Output")

        self.play(Create(image), run_time=2)
        self.play(FadeIn(kernel), FadeIn(output))
        self.play(Convolve(image, kernel, output, cells=[(0, 0), (0, 1), (0, 2), (1, 0)],
                           time_per_cell=1.0))
        self.play(Convolve(image, kernel, output))
        self.wait()


if __name__ == "__main__":
    BoxBlur().render_gif("out/box_blur.gif")
