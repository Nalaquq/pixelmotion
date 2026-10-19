"""Edges are rapid changes: a row of pixels and its first and second derivatives."""

from pixelmotion import *
from pixelmotion.data import edge_signal


class EdgeProfileSlide(Slide):
    title = "Edges = Rapid Changes in Intensity"
    subtitle = "Follow one row of pixels across an edge and measure how fast it changes"
    info = [
        "# 1st derivative",
        "How much brightness changes from one pixel to the next.",
        ("Edge = its peak", ACCENT2),
        "",
        "# 2nd derivative",
        "How fast that change itself changes.",
        ("Edge = zero crossing", GREEN),
        "",
        "~ A blurry edge spreads the peak out: lower and wider.",
    ]

    def construct(self):
        rows = ("image", "intensity", "first", "second")
        area = self.main.inset(0.1)
        sharp = EdgeProfile(edge_signal(32, "step"), area, show=rows)
        blurry = EdgeProfile(edge_signal(32, "ramp", width=8), area, show=rows)

        self.play(Create(sharp), run_time=4)
        self.wait(2)
        self.play(Transform(sharp, blurry), run_time=3)
        self.wait(2)


if __name__ == "__main__":
    EdgeProfileSlide().render_gif("out/edge_profile.gif")
