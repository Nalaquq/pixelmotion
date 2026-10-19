"""Small synthetic images and signals for examples and teaching.

They are generated, so there are no files to download or license.
"""

import numpy as np


def step_edge(size=8, low=40, high=200, at=None, vertical=True):
    """A dark/bright image split by one straight edge."""
    img = np.full((size, size), float(low))
    at = size // 2 if at is None else at
    if vertical:
        img[:, at:] = high
    else:
        img[at:, :] = high
    return img


def shapes(size=96, noise=8.0, seed=0):
    """Gray scene with a rectangle, a disk, a triangle, and one faint ellipse.

    Edges run in every direction and at several contrasts, so gradients,
    NMS, and Canny's weak/strong thresholds all have something to show.
    """
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size] / size
    img = 60 + 40 * xx
    faint = ((xx - 0.2) / 0.12) ** 2 + ((yy - 0.75) / 0.1) ** 2 < 1
    img[faint] += 22
    img[(yy > 0.15) & (yy < 0.45) & (xx > 0.1) & (xx < 0.45)] = 200
    img[(xx - 0.7) ** 2 + (yy - 0.32) ** 2 < 0.17 ** 2] = 150
    tri = (yy > 0.58) & (yy < 0.9) & (np.abs(xx - 0.5) < (yy - 0.58) * 0.9)
    img[tri] = 230
    img += rng.normal(0, noise, img.shape)
    return np.clip(img, 0, 255)


def edge_signal(n=40, kind="step", low=50, high=200, width=6, noise=0.0, seed=0):
    """A 1-D row of pixel intensities crossing an edge.

    ``kind``: "step" (sharp), "ramp" (a smooth, blurry edge about ``width``
    pixels wide), or "line" (a thin bright line).
    """
    x = np.arange(n)
    mid = n / 2
    if kind == "step":
        s = np.where(x < mid, low, high).astype(float)
    elif kind == "ramp":
        s = low + (high - low) / (1 + np.exp(-(x - mid + 0.5) * 8 / width))
    elif kind == "line":
        s = np.full(n, float(low))
        s[int(mid) - 1:int(mid) + 1] = high
    else:
        raise ValueError(f"unknown kind {kind!r}")
    if noise:
        s = s + np.random.default_rng(seed).normal(0, noise, n)
    return s
