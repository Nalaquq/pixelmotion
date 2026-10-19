"""The gradient at every pixel: arrows over an image, and one pixel up close."""

import numpy as np

from pixelmotion import *
from pixelmotion import data, edges


class GradientFieldSlide(Slide):
    title = "The Image Gradient"
    subtitle = "At each pixel, an arrow pointing toward brighter, longer where the change is sharper"
    info = [
        "# Two Sobel filters",
        "$G_x$: change left to right",
        "$G_y$: change top to bottom",
        "",
        "# Combine them",
        (r"Strength $= \sqrt{G_x^2 + G_y^2}$", ACCENT),
        (r"Direction $= \mathrm{atan2}(G_y, G_x)$", ACCENT),
        "",
        "~ Arrows cross edges at right angles.",
    ]

    def construct(self):
        img = data.shapes(64, noise=4)
        gx, gy = edges.sobel(edges.gaussian_blur(img, 1.0))
        pic, diag = self.main.split(2, gap=0.4)
        pic = Region(pic.x, pic.y + 0.4, pic.w, pic.h - 0.8)

        panel = ImagePanel(img, pic, title="Image + gradient arrows")
        field = GradientField.over(panel, gx, gy, step=4, min_strength=0.2)

        def strongest_at(angle):
            """The pixel with the strongest gradient pointing near ``angle``."""
            mag = np.hypot(gx, gy)
            off = np.radians(edges.gradient_direction(gx, gy) - angle)
            return np.unravel_index(np.argmax(mag * np.cos(off).clip(0) ** 8), mag.shape)

        p1, p2 = strongest_at(-40), strongest_at(130)
        spot = diag.center + UP * 1.3
        scale = 1.9 / np.hypot(gx, gy).max()
        d1 = GradientDiagram(gx[p1], gy[p1], center=spot, size=2.4, scale=scale)
        d2 = GradientDiagram(gx[p2], gy[p2], center=spot, size=2.4, scale=scale)
        caption = Text("Gradient at one pixel", size=15, weight="bold")
        caption.next_to(d1, UP, buff=0.35)

        self.play(FadeIn(panel))
        self.play(Create(field), run_time=3)
        self.wait()
        self.play(FadeIn(caption), Create(d1), run_time=3)
        self.wait(2)
        self.play(Transform(d1, d2), run_time=3)
        self.wait(2)


if __name__ == "__main__":
    GradientFieldSlide().render_gif("out/gradient_field.gif")
