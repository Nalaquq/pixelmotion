"""Edges: gradients, Sobel, NMS, hysteresis, Canny, Laplacian, DoG.

Objects and animations to draw, plus the NumPy algorithms that produce the
images they show (``pixelmotion.edges.canny(img)`` keeps every step).
"""

from .animations import Hysteresis, NonMaxSuppression
from .objects import EdgeProfile, GradientDiagram, GradientField
from .ops import (LAPLACIAN, NONE, PREWITT_X, PREWITT_Y, SOBEL_X, SOBEL_Y, STRONG, WEAK,
                  CannySteps, canny, difference_of_gaussians, double_threshold, filter2d,
                  gaussian_blur, gaussian_kernel, gradient_direction, gradient_magnitude,
                  hysteresis, hysteresis_waves, laplacian, nms_neighbors, non_max_suppression,
                  quantize_direction, sobel)

__all__ = [
    # draw
    "EdgeProfile", "GradientDiagram", "GradientField", "Hysteresis", "NonMaxSuppression",
    # kernels and labels
    "LAPLACIAN", "PREWITT_X", "PREWITT_Y", "SOBEL_X", "SOBEL_Y", "NONE", "WEAK", "STRONG",
    # algorithms
    "CannySteps", "canny", "difference_of_gaussians", "double_threshold", "filter2d",
    "gaussian_blur", "gaussian_kernel", "gradient_direction", "gradient_magnitude",
    "hysteresis", "hysteresis_waves", "laplacian", "nms_neighbors", "non_max_suppression",
    "quantize_direction", "sobel",
]
