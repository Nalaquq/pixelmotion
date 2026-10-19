"""Dots, lines, arrows, rectangles, circles, polygons."""

import numpy as np
from matplotlib.patches import Circle as _Circle
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.patches import Polygon as _Polygon

from ..core.mobject import Mobject
from ..theme import ACCENT, ORANGE, TEXT


def _pt(p):
    return np.asarray(p, float).reshape(2)


class Dot(Mobject):
    """A filled point; ``size`` is its diameter in points, so it stays round
    inside stretched panels."""

    def __init__(self, point=(0, 0), size=10, color=ACCENT, edge_color="white", **kwargs):
        super().__init__(**kwargs)
        self.point = _pt(point)
        self.size = size
        self.color = color
        self.edge_color = edge_color

    def own_bbox(self):
        r = self.size / 144
        x, y = self.point
        return (x - r, y - r, x + r, y + r)

    def _shift_self(self, v):
        self.point = self.point + v

    def draw(self, ctx, alpha, progress):
        x, y = ctx.tf(self.point[None, :])[0]
        ctx.ax.plot([x], [y], "o", ms=self.size * np.sqrt(progress), color=self.color,
                    mec=self.edge_color, mew=1.2, alpha=alpha, zorder=4 + self.z)


class Line(Mobject):
    """A straight segment (or polyline through ``points``)."""

    check_labels = True   # labels on top of this line are reported

    def __init__(self, start=(0, 0), end=(1, 0), color=TEXT, stroke=2.0, dashed=False,
                 points=None, **kwargs):
        super().__init__(**kwargs)
        self.points = np.asarray(points if points is not None else [start, end], float)
        self.color = color
        self.stroke = stroke
        self.dashed = dashed

    @property
    def start(self):
        return self.points[0]

    @property
    def end(self):
        return self.points[-1]

    def own_bbox(self):
        p = self.points
        return (p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max())

    def _shift_self(self, v):
        self.points = self.points + v

    def partial_points(self, progress):
        """The first ``progress`` fraction of the path, by length."""
        p = self.points
        if progress >= 1:
            return p
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        target = seg.sum() * progress
        out, run = [p[0]], 0.0
        for a, b, L in zip(p[:-1], p[1:], seg):
            if run + L >= target:
                out.append(a + (b - a) * ((target - run) / L if L else 0))
                break
            out.append(b)
            run += L
        return np.array(out)

    def draw(self, ctx, alpha, progress):
        p = ctx.tf(self.partial_points(progress))
        ctx.ax.plot(p[:, 0], p[:, 1], color=self.color, lw=self.stroke, alpha=alpha,
                    ls="--" if self.dashed else "-", solid_capstyle="round", zorder=2 + self.z)
        if self.check_labels:
            ctx.register_segments(p, self.name or "line")


class Arrow(Line):
    """A straight arrow from ``start`` to ``end``; grows from its tail."""

    def __init__(self, start=(0, 0), end=(1, 0), color=ACCENT, stroke=3.0, head=18, **kwargs):
        super().__init__(start, end, color=color, stroke=stroke, **kwargs)
        self.head = head

    def draw(self, ctx, alpha, progress):
        p = ctx.tf(self.partial_points(progress))
        if np.allclose(p[0], p[-1]):
            return
        ctx.ax.add_patch(FancyArrowPatch(
            tuple(p[0]), tuple(p[-1]), arrowstyle="-|>", mutation_scale=self.head,
            color=self.color, lw=self.stroke, alpha=alpha, shrinkA=0, shrinkB=0,
            linestyle="--" if self.dashed else "-", zorder=3 + self.z))
        if self.check_labels:
            ctx.register_segments(p, self.name or "arrow")


class Polygon(Mobject):
    def __init__(self, *points, color=ACCENT, fill=None, fill_opacity=0.25, stroke=2.0,
                 dashed=False, **kwargs):
        super().__init__(**kwargs)
        self.points = np.asarray(points, float)
        self.color = color
        self.fill_color = fill
        self.fill_opacity = fill_opacity
        self.stroke = stroke
        self.dashed = dashed

    def own_bbox(self):
        p = self.points
        return (p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max())

    def _shift_self(self, v):
        self.points = self.points + v

    def draw(self, ctx, alpha, progress):
        p = ctx.tf(self.points)
        if self.fill_color is not None:
            ctx.ax.add_patch(_Polygon(p, closed=True, facecolor=self.fill_color, edgecolor="none",
                                      alpha=alpha * progress * self.fill_opacity, zorder=1 + self.z))
        if self.color is not None and self.stroke > 0:
            ring = Line(points=np.vstack([self.points, self.points[:1]])).partial_points(progress)
            q = ctx.tf(ring)
            ctx.ax.plot(q[:, 0], q[:, 1], color=self.color, lw=self.stroke, alpha=alpha,
                        ls="--" if self.dashed else "-", zorder=2 + self.z)


class Rectangle(Mobject):
    """Axis-aligned box given by ``center``, ``width``, ``height``.

    ``corner_radius`` > 0 gives the rounded panel look used for info boxes
    (rounded boxes ignore panel transforms).
    """

    def __init__(self, width=2.0, height=1.0, center=(0, 0), color=ACCENT, fill=None,
                 fill_opacity=1.0, stroke=2.0, corner_radius=0.0, dashed=False, **kwargs):
        super().__init__(**kwargs)
        self.center = _pt(center)
        self.size = np.array([width, height], float)
        self.color = color
        self.fill_color = fill
        self.fill_opacity = fill_opacity
        self.stroke = stroke
        self.corner_radius = corner_radius
        self.dashed = dashed

    @classmethod
    def from_corners(cls, x0, y0, x1, y1, **kwargs):
        return cls(x1 - x0, y1 - y0, ((x0 + x1) / 2, (y0 + y1) / 2), **kwargs)

    def corners(self):
        (cx, cy), (w, h) = self.center, self.size / 2
        return np.array([[cx - w, cy - h], [cx + w, cy - h], [cx + w, cy + h], [cx - w, cy + h]])

    def own_bbox(self):
        (cx, cy), (w, h) = self.center, self.size / 2
        return (cx - w, cy - h, cx + w, cy + h)

    def _shift_self(self, v):
        self.center = self.center + v

    def draw(self, ctx, alpha, progress):
        a = alpha * progress
        ls = "--" if self.dashed else "-"
        if self.corner_radius > 0:
            (x0, y0), (w, h) = self.center - self.size / 2, self.size
            r = self.corner_radius
            kw = dict(boxstyle=f"round,pad=0,rounding_size={r}", lw=self.stroke, ls=ls,
                      zorder=1 + self.z)
            if self.fill_color is not None:
                ctx.ax.add_patch(FancyBboxPatch((x0, y0), w, h, facecolor=self.fill_color,
                                                edgecolor="none", alpha=a * self.fill_opacity, **kw))
            if self.color is not None and self.stroke > 0:
                ctx.ax.add_patch(FancyBboxPatch((x0, y0), w, h, facecolor="none",
                                                edgecolor=self.color, alpha=a, **kw))
            return
        p = ctx.tf(self.corners())
        if self.fill_color is not None:
            ctx.ax.add_patch(_Polygon(p, closed=True, facecolor=self.fill_color, edgecolor="none",
                                      alpha=a * self.fill_opacity, zorder=1 + self.z))
        if self.color is not None and self.stroke > 0:
            ctx.ax.add_patch(_Polygon(p, closed=True, facecolor="none", edgecolor=self.color,
                                      lw=self.stroke, ls=ls, alpha=a, zorder=2 + self.z))


def RoundedBox(width=2.0, height=1.0, center=(0, 0), corner_radius=0.15, **kwargs):
    return Rectangle(width, height, center, corner_radius=corner_radius, **kwargs)


def SurroundingRectangle(mobject, buff=0.12, color=ORANGE, stroke=2.5, corner_radius=0.08,
                         **kwargs):
    """A box hugging ``mobject``'s bounding box (``buff`` units of padding)."""
    x0, y0, x1, y1 = mobject.bbox()
    return Rectangle.from_corners(x0 - buff, y0 - buff, x1 + buff, y1 + buff, color=color,
                                  stroke=stroke, corner_radius=corner_radius, **kwargs)


def BackgroundRectangle(mobject, buff=0.15, color="#FFFFFF", opacity=0.92, **kwargs):
    """An opaque, borderless box behind ``mobject`` so it reads over a busy grid.

    Put it first: ``Group(BackgroundRectangle(m), m)``.
    """
    return SurroundingRectangle(mobject, buff=buff, color=None, stroke=0, fill=color,
                                fill_opacity=opacity, **kwargs)


class Circle(Mobject):
    def __init__(self, radius=1.0, center=(0, 0), color=ACCENT, fill=None, fill_opacity=0.25,
                 stroke=2.0, **kwargs):
        super().__init__(**kwargs)
        self.center = _pt(center)
        self.radius = radius
        self.color = color
        self.fill_color = fill
        self.fill_opacity = fill_opacity
        self.stroke = stroke

    def own_bbox(self):
        (x, y), r = self.center, self.radius
        return (x - r, y - r, x + r, y + r)

    def _shift_self(self, v):
        self.center = self.center + v

    def draw(self, ctx, alpha, progress):
        c = ctx.tf(self.center[None, :])[0]
        if self.fill_color is not None:
            ctx.ax.add_patch(_Circle(c, self.radius, facecolor=self.fill_color, edgecolor="none",
                                     alpha=alpha * progress * self.fill_opacity, zorder=1 + self.z))
        if self.stroke > 0:
            th = np.linspace(0, 2 * np.pi * progress, 90)
            ring = c + self.radius * np.c_[np.cos(th), np.sin(th)]
            ctx.ax.plot(ring[:, 0], ring[:, 1], color=self.color, lw=self.stroke, alpha=alpha,
                        zorder=2 + self.z)
