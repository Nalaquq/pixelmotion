"""Animation base class and composition (groups, lagged starts, successions)."""

import numpy as np

from ..rate_functions import linear, smooth

DEFAULT_RUN_TIME = 2.0


class Animation:
    """Changes a mobject over ``run_time`` seconds.

    Subclasses implement ``interpolate(alpha)`` where alpha is eased progress
    in [0, 1]. ``introducer`` animations add their mobject to the scene;
    ``remover`` animations take it out when they finish.
    """

    introducer = False
    remover = False

    def __init__(self, mobject=None, run_time=None, rate_func=smooth):
        self.mobject = mobject
        self.run_time = DEFAULT_RUN_TIME if run_time is None else run_time
        self.rate_func = rate_func

    def begin(self, scene):
        if self.introducer and self.mobject is not None:
            scene.add(self.mobject)
        self.update(0.0)

    def update(self, t):
        self.interpolate(self.rate_func(float(np.clip(t, 0, 1))))

    def interpolate(self, alpha):
        pass

    def finish(self, scene):
        self.update(1.0)
        if self.remover and self.mobject is not None:
            scene.remove(self.mobject)


class AnimationGroup(Animation):
    """Play animations together; each starts ``lag_ratio`` of the previous
    one's run time after it."""

    def __init__(self, *animations, lag_ratio=0.0, run_time=None, rate_func=linear):
        self.animations = [_as_animation(a) for a in animations]
        self.lag_ratio = lag_ratio
        starts, t = [], 0.0
        for a in self.animations:
            starts.append(t)
            t += a.run_time * lag_ratio
        self.starts = np.array(starts)
        natural = max((s + a.run_time for s, a in zip(starts, self.animations)), default=0)
        self.natural = natural or 1e-9
        super().__init__(None, run_time=natural if run_time is None else run_time,
                         rate_func=rate_func)

    def begin(self, scene):
        for a in self.animations:
            a.begin(scene)
        self.update(0.0)

    def interpolate(self, alpha):
        T = alpha * self.natural
        for s, a in zip(self.starts, self.animations):
            a.update((T - s) / a.run_time if a.run_time > 0 else 1.0)

    def finish(self, scene):
        for a in self.animations:
            a.finish(scene)


class LaggedStart(AnimationGroup):
    def __init__(self, *animations, lag_ratio=0.25, **kwargs):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class Succession(AnimationGroup):
    def __init__(self, *animations, **kwargs):
        super().__init__(*animations, lag_ratio=1.0, **kwargs)


def _as_animation(a):
    from .transform import AnimateBuilder
    if isinstance(a, AnimateBuilder):
        return a.build()
    return a
