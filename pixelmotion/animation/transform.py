"""Fades, creation, transforms, and indications.

Each is a transition from a start state to an end state of the same mobject;
``interpolate_mobject`` does the in-between work.
"""

import numpy as np

from ..core.mobject import interpolate_mobject
from ..rate_functions import linear, there_and_back
from ..theme import ORANGE
from .base import Animation


class _Between(Animation):
    """Move ``mobject`` from state ``start`` to state ``end``."""

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, **kwargs)
        self.start = self.end = None

    def setup_states(self):
        """Set ``self.start`` / ``self.end`` (copies) from the live mobject."""
        raise NotImplementedError

    def begin(self, scene):
        self.original = self.mobject.copy()
        self.setup_states()
        super().begin(scene)

    def interpolate(self, alpha):
        self.mobject.become(interpolate_mobject(self.start, self.end, alpha))


class Transform(_Between):
    """Morph ``mobject`` into ``target``; ``mobject`` keeps its identity."""

    def __init__(self, mobject, target, **kwargs):
        super().__init__(mobject, **kwargs)
        self.target = target

    def setup_states(self):
        self.start, self.end = self.mobject.copy(), self.target.copy()


class ReplacementTransform(Transform):
    """Morph ``mobject`` into ``target``, then swap ``target`` into the scene."""

    def finish(self, scene):
        super().finish(scene)
        self.mobject.become(self.original)
        scene.replace(self.mobject, self.target)


class FadeIn(_Between):
    introducer = True

    def __init__(self, mobject, shift=None, **kwargs):
        super().__init__(mobject, **kwargs)
        self.shift_vec = None if shift is None else np.asarray(shift, float)

    def setup_states(self):
        self.end = self.mobject.copy()
        self.start = self.mobject.copy().set_opacity(0)
        if self.shift_vec is not None:
            self.start.shift(-self.shift_vec)


class FadeOut(_Between):
    remover = True

    def __init__(self, mobject, shift=None, **kwargs):
        super().__init__(mobject, **kwargs)
        self.shift_vec = None if shift is None else np.asarray(shift, float)

    def setup_states(self):
        self.start = self.mobject.copy()
        self.end = self.mobject.copy().set_opacity(0)
        if self.shift_vec is not None:
            self.end.shift(self.shift_vec)

    def finish(self, scene):
        super().finish(scene)
        self.mobject.become(self.original)   # usable again if re-added


class Create(_Between):
    """Draw a mobject in: lines grow, text types on, groups appear in order."""

    introducer = True

    def setup_states(self):
        self.end = self.mobject.copy()
        self.start = self.mobject.copy()
        self.start.progress = 0.0


class Write(Create):
    def __init__(self, mobject, rate_func=linear, **kwargs):
        super().__init__(mobject, rate_func=rate_func, **kwargs)


class Uncreate(_Between):
    remover = True

    def setup_states(self):
        self.start = self.mobject.copy()
        self.end = self.mobject.copy()
        self.end.progress = 0.0

    def finish(self, scene):
        super().finish(scene)
        self.mobject.become(self.original)


class Indicate(_Between):
    """Flash a color on and back off."""

    def __init__(self, mobject, color=ORANGE, run_time=1.5, **kwargs):
        super().__init__(mobject, run_time=run_time, rate_func=there_and_back, **kwargs)
        self.color = color

    def setup_states(self):
        self.start = self.mobject.copy()
        self.end = self.mobject.copy().set_color(self.color)

    def finish(self, scene):
        self.mobject.become(self.original)


class AnimateBuilder:
    """Collects method calls on a copy; ``scene.play`` turns it into a Transform.

    ``mob.animate.shift(RIGHT).set_color(RED)`` animates to the result.
    Pass timing with ``mob.animate(run_time=3).shift(RIGHT)``.
    """

    def __init__(self, mobject):
        self._mobject = mobject
        self._target = mobject.copy()
        self._kwargs = {}

    def __call__(self, **kwargs):
        self._kwargs.update(kwargs)
        return self

    def __getattr__(self, name):
        method = getattr(self._target, name)

        def call(*args, **kwargs):
            method(*args, **kwargs)
            return self
        return call

    def build(self):
        return Transform(self._mobject, self._target, **self._kwargs)
