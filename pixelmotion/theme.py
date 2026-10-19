"""Colors, sizes, and timing shared by every scene (mirrors SLIDE_STYLE_GUIDE.md)."""

from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "BG", "TEXT", "SUB", "ACCENT", "ACCENT2", "GREEN", "ORANGE", "PURPLE", "PANEL_BG", "GRID",
    "BLUE", "RED", "GRAY", "LIGHT_GRAY", "WHITE", "BLACK", "CATEGORICAL",
    "ORIGIN", "RIGHT", "LEFT", "UP", "DOWN", "UR", "UL", "DR", "DL",
    "Theme", "DEFAULT_THEME",
]

# ── Palette ──────────────────────────────────────────────────────────────
BG = "#FFFFFF"
TEXT = "#222222"
SUB = "#555555"
ACCENT = "#3498DB"
ACCENT2 = "#E74C3C"
GREEN = "#27AE60"
ORANGE = "#F39C12"
PURPLE = "#9B59B6"
PANEL_BG = "#F8F9FA"
GRID = "#CCCCCC"

BLUE = ACCENT
RED = ACCENT2
GRAY = "#999999"
LIGHT_GRAY = "#E5E7E9"
WHITE = "#FFFFFF"
BLACK = "#000000"

# Cycle for categorical things (rows, classes, clusters)
CATEGORICAL = [ACCENT, ACCENT2, GREEN, ORANGE, PURPLE, "#1ABC9C", "#34495E"]

# ── Directions (canvas units) ────────────────────────────────────────────
ORIGIN = np.array([0.0, 0.0])
RIGHT = np.array([1.0, 0.0])
LEFT = np.array([-1.0, 0.0])
UP = np.array([0.0, 1.0])
DOWN = np.array([0.0, -1.0])
UR, UL, DR, DL = UP + RIGHT, UP + LEFT, DOWN + RIGHT, DOWN + LEFT


@dataclass
class Theme:
    """Everything a scene needs to look like the course slides.

    The canvas is ``width`` x ``height`` units and one unit is one inch of the
    figure, so a 12pt label is 12/72 units tall.
    """

    width: float = 16.0
    height: float = 9.0
    dpi: int = 150
    bg: str = BG
    font_family: str = "sans-serif"

    title_size: float = 30
    subtitle_size: float = 16
    heading_size: float = 17
    body_size: float = 13
    small_size: float = 11

    frame_ms: int = 500          # one animation frame
    hold_ms: int = 800           # default self.wait()
    final_hold_ms: int = 60_000  # last frame of every GIF
    gif_loop: int = 1

    colors: dict = field(default_factory=lambda: {
        "text": TEXT, "sub": SUB, "accent": ACCENT, "accent2": ACCENT2,
        "green": GREEN, "orange": ORANGE, "purple": PURPLE,
        "panel_bg": PANEL_BG, "grid": GRID,
    })

    @property
    def fps(self):
        return 1000 / self.frame_ms


DEFAULT_THEME = Theme()
