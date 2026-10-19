"""Image filtering: kernels and sliding-window convolution."""

from .convolution import Convolve, Kernel, correlate_valid

__all__ = ["Convolve", "Kernel", "correlate_valid"]
