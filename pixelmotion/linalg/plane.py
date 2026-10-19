"""Coordinate planes, vectors, and animated linear transformations."""

import numpy as np

from ..animation.transform import Transform
from ..basics.shapes import Arrow
from ..core.mobject import Mobject
from ..theme import ACCENT, GREEN, GRID, RED, SUB, TEXT


class Vector(Arrow):
    """An arrow from ``start`` (default origin) to ``end``, with an optional label.

    The label sits beside the arrow (``label_side`` +1 = left of the
    direction of travel, -1 = right), ``label_buff`` units off the line, and
    only appears once the arrow has finished growing, so it never lands on
    another label mid-animation.
    """

    def __init__(self, end, start=(0, 0), color=ACCENT, label=None, label_at=0.6,
                 label_side=1, label_buff=0.45, label_size=15, label_color=None, **kwargs):
        super().__init__(start, end, color=color, **kwargs)
        self.label = label
        self.label_at = label_at
        self.label_side = label_side
        self.label_buff = label_buff
        self.label_size = label_size
        self.label_color = label_color

    @property
    def vec(self):
        return self.points[-1] - self.points[0]

    def label_pos(self, tf=None):
        tf = tf or (lambda p: p)
        p = tf(self.points)
        d = p[-1] - p[0]
        n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) or 1)
        return p[0] + d * self.label_at + n * self.label_buff * self.label_side

    def draw(self, ctx, alpha, progress):
        super().draw(ctx, alpha, progress)
        if self.label and progress >= 0.999:
            x, y = self.label_pos(ctx.tf)
            ctx.ax.text(x, y, self.label, fontsize=self.label_size,
                        color=self.label_color or self.color, weight="bold",
                        ha="center", va="center", alpha=alpha, zorder=5)


class Plane(Mobject):
    """A coordinate grid in its own panel; children use plane coordinates.

    Parameters
    ----------
    rect : Region or (x, y, w, h)
        Where the plane goes on the canvas. With ``equal_aspect`` the plane
        is centered in it at the largest size that keeps x and y units equal.
    x_range, y_range : (min, max, step)
    numbers : bool
        Label integer ticks along the axes.

    Notes
    -----
    ``plane.add(Vector((2, 1)))`` draws in plane units. ``apply_matrix(M)``
    warps the grid and everything on it (animate with :class:`ApplyMatrix`).
    """

    def __init__(self, rect, x_range=(-5, 5, 1), y_range=(-4, 4, 1), grid=True, numbers=True,
                 axis_labels=None, equal_aspect=True, grid_color=GRID, ghost=True, **kwargs):
        super().__init__(**kwargs)
        self.rect = np.array(getattr(rect, "rect", rect), float)
        self.x_range = np.array(x_range, float)
        self.y_range = np.array(y_range, float)
        self.grid = grid
        self.numbers = numbers
        self.axis_labels = axis_labels
        self.equal_aspect = equal_aspect
        self.grid_color = grid_color
        self.ghost = ghost
        self.matrix = np.eye(2)

    # ── Coordinates ────────────────────────────────────────────────────
    def axes_rect(self):
        x, y, w, h = self.rect
        if not self.equal_aspect:
            return (x, y, w, h)
        xs = self.x_range[1] - self.x_range[0]
        ys = self.y_range[1] - self.y_range[0]
        s = min(w / xs, h / ys)
        return (x + (w - xs * s) / 2, y + (h - ys * s) / 2, xs * s, ys * s)

    def c2p(self, x, y=None):
        """Plane point -> canvas point (after the current matrix)."""
        p = np.asarray([x, y] if y is not None else x, float) @ self.matrix.T
        ax, ay, aw, ah = self.axes_rect()
        return np.array([ax + (p[0] - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * aw,
                         ay + (p[1] - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * ah])

    def apply_matrix(self, M):
        self.matrix = np.asarray(M, float) @ self.matrix
        return self

    def reset_matrix(self):
        self.matrix = np.eye(2)
        return self

    def basis_vectors(self, i_label=r"$\hat{\imath}$", j_label=r"$\hat{\jmath}$"):
        """The green i-hat and red j-hat vectors (added to the plane)."""
        i = Vector((1, 0), color=GREEN, label=i_label, label_side=-1, label_at=0.5,
                   label_buff=0.35, name="i-hat")
        j = Vector((0, 1), color=RED, label=j_label, label_side=1, label_at=0.5,
                   label_buff=0.35, name="j-hat")
        self.add(i, j)
        return i, j

    def own_bbox(self):
        x, y, w, h = self.rect
        return (x, y, x + w, y + h)

    def bbox(self):
        return self.own_bbox()   # children are in plane units

    def shift(self, *vectors):
        v = np.sum([np.asarray(x, float) for x in vectors], axis=0)
        self.rect = self.rect + np.array([v[0], v[1], 0, 0])
        return self

    # ── Drawing ────────────────────────────────────────────────────────
    def _grid_lines(self, M, color, lw, alpha):
        (x0, x1, dx), (y0, y1, dy) = self.x_range, self.y_range
        ext = 3 * max(x1 - x0, y1 - y0)
        xs = np.arange(np.floor((x0 - ext) / dx) * dx, x1 + ext + 1e-9, dx)
        ys = np.arange(np.floor((y0 - ext) / dy) * dy, y1 + ext + 1e-9, dy)
        segs = [np.array([[x, y0 - ext], [x, y1 + ext]]) for x in xs] + \
               [np.array([[x0 - ext, y], [x1 + ext, y]]) for y in ys]
        return [(s @ M.T, color, lw, alpha) for s in segs]

    def render(self, ctx, opacity=1.0, progress=1.0):
        if self._crossfade is not None:
            return super().render(ctx, opacity, progress)
        alpha = opacity * self.opacity
        p = progress * self.progress
        if alpha <= 0.003 or p <= 0:
            return
        ax = ctx.new_axes(self.axes_rect())
        ax.set_xlim(*self.x_range[:2])
        ax.set_ylim(*self.y_range[:2])
        ax.set_autoscale_on(False)
        ax.axis("off")
        ax.patch.set_alpha(0)
        M = self.matrix
        lines = []
        moved = not np.allclose(M, np.eye(2))
        if self.grid and self.ghost and moved:
            lines += self._grid_lines(np.eye(2), self.grid_color, 0.8, 0.35)
        if self.grid:
            lines += self._grid_lines(M, ACCENT if moved else self.grid_color, 1.0,
                                      0.5 if moved else 0.9)
        big = 3 * max(np.ptp(self.x_range[:2]), np.ptp(self.y_range[:2]))
        for axis in (np.array([[-big, 0], [big, 0]]), np.array([[0, -big], [0, big]])):
            lines.append((axis @ M.T, TEXT, 1.6, 1.0))
        for seg, color, lw, a in lines:
            ax.plot(seg[:, 0], seg[:, 1], color=color, lw=lw, alpha=a * alpha * p, zorder=1)
        if self.numbers and p >= 1:
            (x0, x1, dx), (y0, y1, dy) = self.x_range, self.y_range
            for x in np.arange(np.ceil(x0 / dx) * dx, x1 + 1e-9, dx):
                if abs(x) > 1e-9 and x0 < x < x1:
                    q = np.array([x, 0]) @ M.T
                    ax.text(q[0], q[1] - 0.12 * dy, f"{x:g}".replace("-", "−"),
                            fontsize=10, color=SUB, ha="center", va="top", alpha=alpha)
            for y in np.arange(np.ceil(y0 / dy) * dy, y1 + 1e-9, dy):
                if abs(y) > 1e-9 and y0 < y < y1:
                    q = np.array([0, y]) @ M.T
                    ax.text(q[0] - 0.12 * dx, q[1], f"{y:g}".replace("-", "−"),
                            fontsize=10, color=SUB, ha="right", va="center", alpha=alpha)
        if self.axis_labels:
            xl, yl = self.axis_labels
            ax.text(self.x_range[1], 0.25 * self.y_range[2], xl, fontsize=13,
                    color=SUB, ha="right", va="bottom", alpha=alpha)
            ax.text(0.25 * self.x_range[2], self.y_range[1], yl, fontsize=13, color=SUB,
                    ha="left", va="top", alpha=alpha)
        with ctx.using(ax, tf=lambda P: np.asarray(P, float) @ M.T):
            self.render_children(ctx, alpha, p)


def ApplyMatrix(plane, matrix, **kwargs):
    """Animate the plane (and everything on it) through the linear map ``matrix``."""
    return Transform(plane, plane.copy().apply_matrix(matrix), **kwargs)
