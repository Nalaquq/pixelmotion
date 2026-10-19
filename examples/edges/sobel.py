"""Sobel X as a sliding window over a vertical edge."""

from pixelmotion import *
from pixelmotion.data import step_edge
from pixelmotion.edges import SOBEL_X


class SobelX(Slide):
    title = "Sobel X: Measuring Left-to-Right Change"
    subtitle = "Right column minus left column, with the middle row counted twice"
    info = [
        "# The kernel",
        "Negative weights on the left, positive on the right.",
        "",
        "# Flat regions",
        "Left and right cancel, so the output is 0.",
        "",
        "# At the edge",
        ("Large positive output", RED),
        "~ Red = brighter to the right, blue = darker to the right.",
    ]

    def construct(self):
        img = step_edge(7, low=40, high=200, at=4)
        left, mid, right = self.main.split(3, gap=0.25)
        image = PixelGrid(img, center=left.center, cell=0.5, label="Image")
        kernel = Kernel(SOBEL_X, center=mid.center, label="Sobel X")
        output = PixelGrid.empty((5, 5), center=right.center, cell=0.5, cmap="RdBu_r",
                                 vmin=-900, vmax=900, label="Output (Gx)")

        self.play(FadeIn(image), FadeIn(kernel), FadeIn(output), lag_ratio=0.4)
        self.play(Convolve(image, kernel, output, cells=[(0, 0), (0, 1), (0, 2)],
                           time_per_cell=1.5))
        self.play(Convolve(image, kernel, output, time_per_cell=0.4))
        self.wait(2)


if __name__ == "__main__":
    SobelX().render_gif("out/sobel.gif")
