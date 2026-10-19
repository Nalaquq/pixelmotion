"""PCA step 1: mean-centering a data matrix.

Port of make_slide2() in cv_course/scripts/generate_pca_matrix_slides.py
(~230 lines of phase bookkeeping) to pixelmotion.
"""

import numpy as np

from pixelmotion import *

PEOPLE = [ACCENT2, GREEN, PURPLE]


class MeanCentering(Slide):
    title = "Step 1: Mean-Centering the Data"
    subtitle = "Subtract the column mean from every element, so the data is centred around zero"
    info = [
        "# Why centre?",
        "PCA finds directions of maximum variance.",
        "Variance is measured relative to the mean, so we remove it first.",
        "",
        "# For each column:",
        ("E(h) = 170 cm", GREEN),
        ("E(w) =  60 kg", PURPLE),
        "",
        "~ Subtract these from every row.",
    ]

    def construct(self):
        data = np.array([[150, 50], [170, 70], [190, 60]])
        means = np.tile(data.mean(axis=0), (3, 1))

        X = Matrix(data, label="$X$", col_labels=["height", "weight"], colors=PEOPLE, size=22)
        minus = Text("$-$", size=34)
        M = Matrix(means, label="column means", col_labels=["E(h)", "E(w)"],
                   colors=[[GREEN, PURPLE]] * 3, size=22)
        equals = Text("$=$", size=34)
        result = Matrix(data - means, label=r"$\tilde{X}$", col_labels=["height", "weight"],
                        colors=PEOPLE, signed=True, size=22)

        row = Group(X, minus, M, equals, result).arrange(RIGHT, buff=0.45)
        row.move_to(self.main).shift(UP * 0.8)

        self.play(FadeIn(X, shift=DOWN * 0.3))
        self.play(FadeIn(minus), FadeIn(M), lag_ratio=0.5)
        self.play(FadeIn(equals), run_time=1)

        # X's numbers appear in the result slot, then count down to the centred values.
        moving = X.copy().move_to(result).set_label(r"$\tilde{X}$")
        self.play(FadeIn(moving, shift=RIGHT * 0.3), run_time=1)
        self.play(Transform(moving, result), run_time=4)
        self.wait()

        note = Text("Each column of $\\tilde{X}$ now averages to zero", size=16, color=SUB,
                    style="italic")
        note.next_to(row, DOWN, buff=0.9)
        self.play(moving.animate.highlight_col(0).highlight_col(1, color=ORANGE), FadeIn(note))
        self.wait(2)


if __name__ == "__main__":
    MeanCentering().render_gif("out/mean_centering.gif")
