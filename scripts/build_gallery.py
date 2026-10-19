"""Render every example into docs/assets/gallery/ for the documentation site.

Run before ``mkdocs serve`` / ``mkdocs build``:

    python scripts/build_gallery.py            # all examples
    python scripts/build_gallery.py box_blur   # just one
"""

import dataclasses
import importlib.util
import inspect
import sys
from pathlib import Path

from pixelmotion import DEFAULT_THEME, Scene

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "gallery"
DPI = 80   # small enough for the web, sharp enough to read
# Web pages loop forever with a short pause; classroom GIFs play once and hold.
WEB_THEME = dataclasses.replace(DEFAULT_THEME, gif_loop=0, final_hold_ms=3000)


def scenes_in(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if issubclass(obj, Scene) and obj.__module__ == mod.__name__:
            yield obj


def main(only=()):
    OUT.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / "examples").rglob("*.py")):
        if only and path.stem not in only:
            continue
        for scene_cls in scenes_in(path):
            scene_cls(theme=WEB_THEME).render_gif(str(OUT / f"{path.stem}.gif"), dpi=DPI)


if __name__ == "__main__":
    main(sys.argv[1:])
