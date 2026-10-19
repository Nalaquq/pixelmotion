"""pixelmotion: manim-style animated slides for math and computer vision.

``from pixelmotion import *`` brings in everything, like manim. The same
names are also available by domain, e.g. ``pixelmotion.linalg.Matrix``.
"""

import matplotlib

matplotlib.use("Agg")

from . import rate_functions  # noqa: E402
from .animation import *  # noqa: E402,F401,F403
from .basics import *  # noqa: E402,F401,F403
from .core import *  # noqa: E402,F401,F403
from .filters import *  # noqa: E402,F401,F403
from .image import *  # noqa: E402,F401,F403
from .linalg import *  # noqa: E402,F401,F403
from .rate_functions import linear, smooth, there_and_back  # noqa: E402,F401
from .slide import *  # noqa: E402,F401,F403
from .theme import *  # noqa: E402,F401,F403

__version__ = "0.1.0"
