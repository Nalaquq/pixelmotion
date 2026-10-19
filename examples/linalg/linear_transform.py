"""A matrix as a linear transformation: watch the grid and basis vectors move."""

import numpy as np

from pixelmotion import *


class LinearTransform(Slide):
    title = "A Matrix Moves Space"
    subtitle = "The columns of the matrix say where the basis vectors land"
    info = [
        "# Shear",
        "$\\hat{\\imath}$ stays at (1, 0).",
        "$\\hat{\\jmath}$ moves to (1, 1).",
        "",
        "Every other point follows, so grid lines stay parallel and evenly spaced.",
    ]

    def construct(self):
        M = np.array([[1, 1], [0, 1]])
        plane = Plane(self.main.inset(0.2), x_range=(-4, 4, 1), y_range=(-3, 3, 1))
        plane.basis_vectors()
        v = Vector((2, 1), color=ORANGE, label="v", name="v")
        plane.add(v)

        mat = Matrix(M, label="M", size=22, colors=[[GREEN, RED]] * 2)
        mat.move_to(plane.c2p(-3.0, 2.0))
        mat_card = Group(BackgroundRectangle(mat), mat)

        self.play(Create(plane), run_time=2)
        self.play(FadeIn(mat_card))
        self.play(ApplyMatrix(plane, M), run_time=4)
        self.wait(2)


if __name__ == "__main__":
    LinearTransform().render_gif("out/linear_transform.gif")
