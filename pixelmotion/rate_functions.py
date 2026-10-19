"""Easing curves mapping linear time t in [0, 1] to animation progress."""

import numpy as np


def linear(t):
    return t


def smooth(t):
    """Smoothstep: slow in, slow out (manim's default feel)."""
    return t * t * (3 - 2 * t)


def rush_into(t):
    return 2 * smooth(t / 2)


def rush_from(t):
    return 2 * smooth(t / 2 + 0.5) - 1


def there_and_back(t):
    """0 -> 1 -> 0; used by indication animations."""
    return smooth(1 - abs(2 * t - 1))


def stepped(n):
    """Snap progress to n discrete steps (for cell-by-cell sweeps)."""
    def f(t):
        return np.floor(t * n + 1e-9) / n
    return f
