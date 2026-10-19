"""Mobject: anything that can be drawn in a scene and animated.

Drawing is immediate-mode: every frame the scene clears the figure and asks
each mobject to draw itself from its current attributes. Animations therefore
only need to change attributes; Transform interpolates them generically.
"""

import copy

import numpy as np
from matplotlib.colors import to_hex, to_rgb

from ..theme import DEFAULT_THEME, RIGHT


class Mobject:
    """Base for everything drawable.

    Children live only in ``self.submobjects``; expose views of them through
    properties rather than storing extra references, so copies and
    ``become`` keep one consistent family tree.
    """

    # Attribute names shared (not copied) between frame snapshots, e.g. large
    # image arrays. Replace them rather than mutating them in place.
    _no_copy = ("updaters",)

    def __init__(self, opacity=1.0, z=0, name=None):
        self.opacity = opacity
        self.progress = 1.0   # 0..1, how much of the mobject is "drawn in"
        self.z = z
        self.name = name
        self.submobjects = []
        self.updaters = []
        self._crossfade = None  # (start, end, alpha) while Transform can't lerp

    # ── Structure ──────────────────────────────────────────────────────
    def add(self, *mobjects):
        for m in mobjects:
            if m not in self.submobjects:
                self.submobjects.append(m)
        return self

    def remove(self, *mobjects):
        self.submobjects = [m for m in self.submobjects if m not in mobjects]
        return self

    def family(self):
        """This mobject and every descendant."""
        out = [self]
        for m in self.submobjects:
            out.extend(m.family())
        return out

    def __iter__(self):
        return iter(self.submobjects)

    def __len__(self):
        return len(self.submobjects)

    def __getitem__(self, i):
        return self.submobjects[i]

    # ── Copying ────────────────────────────────────────────────────────
    def copy(self):
        new = self.__class__.__new__(self.__class__)
        for k, v in self.__dict__.items():
            new.__dict__[k] = v if k in self._no_copy else _copy_value(v)
        return new

    def become(self, other):
        """Take on another mobject's state while keeping this identity (and,
        where the structure matches, the identity of every child)."""
        self._adopt(other.copy())
        return self

    def _adopt(self, fresh):
        old_children, updaters = self.submobjects, self.updaters
        self.__dict__ = fresh.__dict__
        self.updaters = updaters
        new_children = self.submobjects
        if len(old_children) == len(new_children) and all(
                type(o) is type(n) for o, n in zip(old_children, new_children)):
            for o, n in zip(old_children, new_children):
                o._adopt(n)
            self.submobjects = old_children

    # ── Geometry (canvas or parent-panel units) ────────────────────────
    def own_bbox(self):
        """(x0, y0, x1, y1) of what this mobject draws itself, or None."""
        return None

    def bbox(self):
        boxes = [b for b in [self.own_bbox()] + [m.bbox() for m in self.submobjects]
                 if b is not None]
        if not boxes:
            return None
        b = np.array(boxes)
        return (b[:, 0].min(), b[:, 1].min(), b[:, 2].max(), b[:, 3].max())

    def get_center(self):
        x0, y0, x1, y1 = self.bbox()
        return np.array([(x0 + x1) / 2, (y0 + y1) / 2])

    @property
    def width(self):
        x0, _, x1, _ = self.bbox()
        return x1 - x0

    @property
    def height(self):
        _, y0, _, y1 = self.bbox()
        return y1 - y0

    def get_edge(self, direction):
        """Point on the bounding box in ``direction`` (e.g. UP, DR)."""
        x0, y0, x1, y1 = self.bbox()
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        half = np.array([(x1 - x0) / 2, (y1 - y0) / 2])
        return c + np.sign(np.asarray(direction, float)) * half

    def get_top(self):
        return self.get_edge((0, 1))

    def get_bottom(self):
        return self.get_edge((0, -1))

    def get_left(self):
        return self.get_edge((-1, 0))

    def get_right(self):
        return self.get_edge((1, 0))

    def _shift_self(self, v):
        """Move this mobject's own points by v (subclasses override)."""

    def shift(self, *vectors):
        v = np.sum([np.asarray(x, float) for x in vectors], axis=0)
        self._shift_self(v)
        for m in self.submobjects:
            m.shift(v)
        return self

    def move_to(self, target, aligned_edge=None):
        """Center on ``target`` (point, mobject, or Region), or line up an edge."""
        if aligned_edge is None:
            return self.shift(_as_point(target) - self.get_center())
        if isinstance(target, Mobject):
            point = target.get_edge(aligned_edge)
        else:
            point = _as_point(target)
        return self.shift(point - self.get_edge(aligned_edge))

    def next_to(self, other, direction=RIGHT, buff=0.25, aligned_edge=None):
        """Place this mobject ``buff`` units beside ``other`` (mobject or point).

        Off the ``direction`` axis the two are centered, or share
        ``aligned_edge`` (e.g. ``next_to(a, DOWN, aligned_edge=LEFT)``).
        """
        direction = np.asarray(direction, float)
        is_mob = isinstance(other, Mobject)
        anchor = other.get_edge(direction) if is_mob else np.asarray(other, float)
        delta = anchor - self.get_edge(-direction) + direction * buff
        perp = direction == 0
        if aligned_edge is not None and is_mob:
            delta[perp] = (other.get_edge(aligned_edge) - self.get_edge(aligned_edge))[perp]
        else:
            ref = other.get_center() if is_mob else anchor
            delta[perp] = (ref - self.get_center())[perp]
        return self.shift(delta)

    # ── Styling ────────────────────────────────────────────────────────
    def set_opacity(self, opacity):
        self.opacity = opacity
        return self

    def set_color(self, color):
        if hasattr(self, "color"):
            self.color = color
        for m in self.submobjects:
            m.set_color(color)
        return self

    def set_z(self, z):
        self.z = z
        return self

    # ── Updaters ───────────────────────────────────────────────────────
    def add_updater(self, fn):
        """``fn(mobject)`` runs before every frame is captured."""
        self.updaters = self.updaters + [fn]
        return self

    def clear_updaters(self):
        self.updaters = []
        return self

    def update(self):
        for fn in self.updaters:
            fn(self)
        for m in self.submobjects:
            m.update()

    # ── Animation sugar ────────────────────────────────────────────────
    @property
    def animate(self):
        """``self.play(mob.animate.shift(RIGHT).set_color(RED))``"""
        from ..animation.transform import AnimateBuilder
        return AnimateBuilder(self)

    # ── Drawing ────────────────────────────────────────────────────────
    def render(self, ctx, opacity=1.0, progress=1.0):
        if self._crossfade is not None:
            start, end, a = self._crossfade
            start.render(ctx, opacity * (1 - a), progress)
            end.render(ctx, opacity * a, progress)
            return
        alpha = opacity * self.opacity
        p = progress * self.progress
        if alpha <= 0.003 or p <= 0:
            return
        self.draw(ctx, alpha, p)
        self.render_children(ctx, alpha, p)

    def render_children(self, ctx, alpha, progress):
        """Children draw in sequence as ``progress`` goes 0 -> 1."""
        n = len(self.submobjects)
        for i, m in enumerate(sorted(self.submobjects, key=lambda m: m.z)):
            child_p = 1.0 if progress >= 1 else float(np.clip(progress * n - i, 0, 1))
            m.render(ctx, alpha, child_p)

    def draw(self, ctx, alpha, progress):
        """Draw this mobject's own artists onto ``ctx.ax``."""

    @property
    def theme(self):
        return DEFAULT_THEME

    def __repr__(self):
        return f"<{self.__class__.__name__}{' ' + self.name if self.name else ''}>"


class Group(Mobject):
    """A container; transforms and animations apply to all children."""

    def __init__(self, *mobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*mobjects)

    def arrange(self, direction=RIGHT, buff=0.3, center=True):
        """Lay children out in a row/column, each ``buff`` from the last."""
        if not self.submobjects:
            return self
        c = self.get_center()
        for prev, m in zip(self.submobjects, self.submobjects[1:]):
            m.next_to(prev, direction, buff)
        if center:
            self.move_to(c)
        return self


class ValueTracker(Mobject):
    """An invisible number to animate; other mobjects read it in updaters."""

    def __init__(self, value=0.0):
        super().__init__()
        self.value = float(value)

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = float(value)
        return self

    def increment_value(self, dv):
        self.value += dv
        return self


# ── Helpers ───────────────────────────────────────────────────────────────

def _as_point(target):
    if isinstance(target, Mobject):
        return target.get_center()
    if hasattr(target, "center") and not isinstance(target, np.ndarray):
        return np.asarray(target.center, float)   # Region
    return np.asarray(target, float)


def _copy_value(v):
    if isinstance(v, Mobject):
        return v.copy()
    if isinstance(v, np.ndarray):
        return v.copy()
    if isinstance(v, list):
        return [_copy_value(x) for x in v]
    if isinstance(v, tuple):
        return tuple(_copy_value(x) for x in v)
    if isinstance(v, dict):
        return {k: _copy_value(x) for k, x in v.items()}
    if callable(v):
        return v
    return copy.deepcopy(v)


class _Incompatible(Exception):
    pass


def interpolate_mobject(start, end, alpha):
    """A new mobject part-way from ``start`` to ``end``.

    Numbers, arrays, and ``*color*`` attributes are interpolated; children
    are matched pairwise. Any mobject whose non-numeric state differs (e.g.
    different text) becomes a cross-fade between its two versions.
    """
    if alpha <= 0:
        return start.copy()
    if alpha >= 1:
        return end.copy()
    if type(start) is not type(end):
        return _crossfade(start, end, alpha)
    new = start.__class__.__new__(start.__class__)
    try:
        for k in set(start.__dict__) | set(end.__dict__):
            if k in ("_crossfade",):
                new.__dict__[k] = None
                continue
            if k not in start.__dict__ or k not in end.__dict__:
                raise _Incompatible(k)
            a, b = start.__dict__[k], end.__dict__[k]
            if k == "updaters":
                new.__dict__[k] = a
            elif k in start._no_copy:
                if a is not b:      # e.g. two different images: cross-fade
                    raise _Incompatible(k)
                new.__dict__[k] = a
            else:
                new.__dict__[k] = _lerp(a, b, alpha, k)
    except _Incompatible:
        return _crossfade(start, end, alpha)
    return new


def _crossfade(start, end, alpha):
    new = start.copy()
    new._crossfade = (start.copy(), end.copy(), alpha)
    return new


def _lerp(a, b, alpha, key):
    if isinstance(a, Mobject) and isinstance(b, Mobject):
        return interpolate_mobject(a, b, alpha)
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a_arr, b_arr = np.asarray(a), np.asarray(b)
        if a_arr.shape != b_arr.shape:
            raise _Incompatible(key)
        if a_arr.dtype.kind in "fiu" and b_arr.dtype.kind in "fiu":
            return a_arr + (b_arr - a_arr) * alpha
        if np.array_equal(a_arr, b_arr):
            return a_arr.copy()
        raise _Incompatible(key)
    if isinstance(a, bool) or isinstance(b, bool):
        return b if alpha >= 0.5 else a     # flags (signed, dashed...) switch halfway
    if isinstance(a, int) and isinstance(b, int):
        return a if a == b else int(round(a + (b - a) * alpha))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * alpha
    if "color" in key and isinstance(a, str) and isinstance(b, str):
        if a == b:
            return a
        ra, rb = np.array(to_rgb(a)), np.array(to_rgb(b))
        return to_hex(ra + (rb - ra) * alpha)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            raise _Incompatible(key)
        out = [_lerp(x, y, alpha, key) for x, y in zip(a, b)]
        return out if isinstance(a, list) else tuple(out)
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            raise _Incompatible(key)
        return {k: _lerp(a[k], b[k], alpha, key) for k in a}
    if callable(a) or callable(b):
        return b if alpha >= 0.5 else a
    if a == b:
        return copy.deepcopy(a)
    raise _Incompatible(key)
