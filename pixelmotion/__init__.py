"""pixelmotion: manim-style animated slides for math and computer vision.

``from pixelmotion import *`` brings in every drawable object and animation,
like manim. Everything is also available by domain, e.g.
``pixelmotion.linalg.Matrix``; algorithms live in their domain
(``pixelmotion.edges.canny``) and sample images in ``pixelmotion.data``.
"""

import matplotlib

matplotlib.use("Agg")

from . import data, edges, rate_functions  # noqa: E402,F401
from .animation import *  # noqa: E402,F401,F403
from .basics import *  # noqa: E402,F401,F403
from .core import *  # noqa: E402,F401,F403
from .edges import (EdgeProfile, GradientDiagram, GradientField, Hysteresis,  # noqa: E402,F401
                    NonMaxSuppression)
from .filters import *  # noqa: E402,F401,F403
from .image import *  # noqa: E402,F401,F403
from .linalg import *  # noqa: E402,F401,F403
from .rate_functions import linear, smooth, there_and_back  # noqa: E402,F401
from .slide import *  # noqa: E402,F401,F403
from .theme import *  # noqa: E402,F401,F403

__version__ = "0.1.0"
