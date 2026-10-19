"""Edge-detection math in plain NumPy, with every Canny step exposed.

These return arrays to show with ImagePanel / PixelGrid, and drive the edge
animations. They favor clarity over speed; slide images are small.
"""

from dataclasses import dataclass

import numpy as np

SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)
SOBEL_Y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], float)
"""Sobel kernels. ``SOBEL_X`` responds to vertical edges (left-right change);
``SOBEL_Y`` is written for image rows growing downward, so it responds to
horizontal edges with bright-below positive."""

PREWITT_X = np.array([[-1, 0, 1]] * 3, float)
PREWITT_Y = PREWITT_X.T.copy()
LAPLACIAN = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)

# Pixel states after double thresholding
NONE, WEAK, STRONG = 0, 1, 2


def filter2d(image, kernel, mode="same"):
    """Slide ``kernel`` over ``image`` (cross-correlation, like OpenCV).

    ``mode="same"`` pads edges by repeating border pixels and keeps the
    image size; ``mode="valid"`` keeps only full-overlap positions.
    """
    image = np.asarray(image, float)
    kernel = np.asarray(kernel, float)
    kh, kw = kernel.shape
    if mode == "same":
        image = np.pad(image, ((kh // 2, kh - 1 - kh // 2), (kw // 2, kw - 1 - kw // 2)),
                       mode="edge")
    H, W = image.shape[0] - kh + 1, image.shape[1] - kw + 1
    out = np.zeros((H, W))
    for i in range(kh):
        for j in range(kw):
            out += kernel[i, j] * image[i:i + H, j:j + W]
    return out


def gaussian_kernel(sigma=1.0, size=None):
    """Normalized 2-D Gaussian; ``size`` defaults to about 6 sigma, odd."""
    if size is None:
        size = int(2 * np.ceil(3 * sigma) + 1)
    r = np.arange(size) - (size - 1) / 2
    g = np.exp(-r ** 2 / (2 * sigma ** 2))
    k = np.outer(g, g)
    return k / k.sum()


def gaussian_blur(image, sigma=1.0):
    return filter2d(image, gaussian_kernel(sigma))


def sobel(image):
    """``(gx, gy)``: horizontal and vertical intensity change at each pixel."""
    return filter2d(image, SOBEL_X), filter2d(image, SOBEL_Y)


def gradient_magnitude(gx, gy):
    return np.hypot(gx, gy)


def gradient_direction(gx, gy):
    """Gradient angle in degrees, in image coordinates (y down), -180..180."""
    return np.degrees(np.arctan2(gy, gx))


def quantize_direction(angle):
    """Snap angles to the 4 NMS directions: 0 (horizontal), 45, 90, 135."""
    a = np.mod(angle, 180)
    return (np.round(a / 45) % 4 * 45).astype(int)


# Neighbour offsets (drow, dcol) along each quantized gradient direction.
# Angles come from arctan2(gy, gx) with rows growing downward, so 45 deg
# points right and down the image: (+1 row, +1 col).
NMS_OFFSETS = {0: (0, 1), 45: (1, 1), 90: (1, 0), 135: (1, -1)}


def nms_neighbors(r, c, angle):
    """The two pixels NMS compares ``(r, c)`` against, for gradient ``angle``."""
    dr, dc = NMS_OFFSETS[int(quantize_direction(angle))]
    return (r + dr, c + dc), (r - dr, c - dc)


def non_max_suppression(magnitude, angle):
    """Keep a pixel only if it is the strongest of itself and its two
    neighbours along the gradient direction (thins edges to one pixel)."""
    H, W = magnitude.shape
    out = np.zeros_like(magnitude, dtype=float)
    q = quantize_direction(angle)
    for r in range(1, H - 1):
        for c in range(1, W - 1):
            dr, dc = NMS_OFFSETS[int(q[r, c])]
            m = magnitude[r, c]
            # ">" on one side breaks ties, so a symmetric ridge stays 1 px wide
            if m > magnitude[r + dr, c + dc] and m >= magnitude[r - dr, c - dc]:
                out[r, c] = m
    return out


def double_threshold(image, low, high):
    """Label pixels NONE / WEAK / STRONG (0 / 1 / 2)."""
    labels = np.full(image.shape, NONE, int)
    labels[image >= low] = WEAK
    labels[image >= high] = STRONG
    return labels


def hysteresis_waves(labels):
    """Grow strong edges into connected weak pixels, one ring at a time.

    Returns a list of label arrays: the input, then one array per wave of
    promotion (8-connected). The last array has no WEAK pixels left that
    touch an edge; leftover weak pixels are dropped by :func:`hysteresis`.
    """
    cur = np.array(labels, int)
    waves = [cur.copy()]
    while True:
        strong = cur == STRONG
        grown = np.zeros_like(strong)
        H, W = strong.shape
        p = np.pad(strong, 1)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                grown |= p[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]
        promote = grown & (cur == WEAK)
        if not promote.any():
            return waves
        cur = cur.copy()
        cur[promote] = STRONG
        waves.append(cur.copy())


def hysteresis(labels):
    """Final edge map (bool): strong pixels plus weak ones connected to them."""
    return hysteresis_waves(labels)[-1] == STRONG


def laplacian(image):
    return filter2d(image, LAPLACIAN)


def difference_of_gaussians(image, sigma1=1.0, sigma2=2.0):
    """``G(sigma1) - G(sigma2)``: a band-pass that approximates the LoG."""
    return gaussian_blur(image, sigma1) - gaussian_blur(image, sigma2)


@dataclass
class CannySteps:
    """Every intermediate image of :func:`canny`, in pipeline order."""

    image: np.ndarray
    blurred: np.ndarray
    gx: np.ndarray
    gy: np.ndarray
    magnitude: np.ndarray
    direction: np.ndarray
    nms: np.ndarray
    labels: np.ndarray
    edges: np.ndarray

    def stages(self):
        """``[(title, image, kind)]`` for an ImagePipeline; ``kind`` is
        "gray", "signed" (diverging colors), or "labels"."""
        return [
            ("Input", self.image, "gray"),
            ("1. Gaussian blur", self.blurred, "gray"),
            ("2. Gradient magnitude", self.magnitude, "gray"),
            ("3. Non-max suppression", self.nms, "gray"),
            ("4. Double threshold", self.labels, "labels"),
            ("5. Hysteresis", self.edges.astype(float), "gray"),
        ]


def canny(image, sigma=1.4, low=0.12, high=0.35):
    """Canny edge detection with every step kept.

    ``low`` and ``high`` are fractions of the strongest NMS response.
    """
    image = np.asarray(image, float)
    blurred = gaussian_blur(image, sigma)
    gx, gy = sobel(blurred)
    mag = gradient_magnitude(gx, gy)
    ang = gradient_direction(gx, gy)
    thin = non_max_suppression(mag, ang)
    peak = thin.max() or 1.0
    labels = double_threshold(thin, low * peak, high * peak)
    return CannySteps(image, blurred, gx, gy, mag, ang, thin, labels, hysteresis(labels))
