"""Generic animations that work on any mobject."""

from .base import Animation, AnimationGroup, LaggedStart, Succession
from .transform import (Create, FadeIn, FadeOut, Indicate, ReplacementTransform, Transform,
                        Uncreate, Write)

__all__ = ["Animation", "AnimationGroup", "LaggedStart", "Succession", "Create", "FadeIn",
           "FadeOut", "Indicate", "ReplacementTransform", "Transform", "Uncreate", "Write"]
