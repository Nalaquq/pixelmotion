"""Scene: build an animation step by step, then render it to GIF or PNG."""

import os
import re
import warnings

from ..animation.base import AnimationGroup, _as_animation
from ..theme import DEFAULT_THEME
from .canvas import FrameRenderer
from .overlap import OverlapReport, check_frame


class OverlapError(RuntimeError):
    pass


class Scene:
    """Subclass and implement :meth:`construct`, like a manim scene.

    Example
    -------
    >>> class Hello(Scene):
    ...     def construct(self):
    ...         t = Text("Hello")
    ...         self.play(FadeIn(t))
    ...         self.wait()
    >>> Hello().render_gif("hello.gif")

    ``construct`` only records frames (cheap snapshots of every mobject);
    pixels are produced when you call a ``render_*`` method.
    """

    theme = DEFAULT_THEME

    def __init__(self, theme=None):
        if theme is not None:
            self.theme = theme
        self.mobjects = []
        self._timeline = []     # [(snapshot list, duration_ms)]
        self._built = False
        self.overlap_report = None

    # ── Authoring API ──────────────────────────────────────────────────
    def setup(self):
        """Runs before :meth:`construct`; :class:`Slide` adds its chrome here."""

    def construct(self):
        raise NotImplementedError("Implement construct() in your Scene subclass.")

    def add(self, *mobjects):
        """Show mobjects immediately (no animation)."""
        for m in mobjects:
            if m not in self.mobjects:
                self.mobjects.append(m)
        return self

    def remove(self, *mobjects):
        self.mobjects = [m for m in self.mobjects if m not in mobjects]
        return self

    def replace(self, old, new):
        if old in self.mobjects:
            self.mobjects[self.mobjects.index(old)] = new
        else:
            self.add(new)
        return self

    def clear(self):
        self.mobjects = []
        return self

    def play(self, *animations, run_time=None, rate_func=None, lag_ratio=0.0):
        """Run animations together and record their frames.

        Accepts animations or ``mob.animate`` chains. ``run_time`` (seconds)
        overrides the animations' own; frames last ``theme.frame_ms`` each.
        """
        anims = [_as_animation(a) for a in animations]
        anim = anims[0] if len(anims) == 1 and lag_ratio == 0 else \
            AnimationGroup(*anims, lag_ratio=lag_ratio)
        if run_time is not None:
            anim.run_time = run_time
        if rate_func is not None:
            anim.rate_func = rate_func
        anim.begin(self)
        n = max(1, round(anim.run_time * 1000 / self.theme.frame_ms))
        for i in range(1, n + 1):
            anim.update(i / n)
            self._capture(self.theme.frame_ms)
        anim.finish(self)

    def wait(self, seconds=None):
        """Hold the current frame (default ``theme.hold_ms``)."""
        ms = self.theme.hold_ms if seconds is None else int(seconds * 1000)
        self._capture(ms)

    def _capture(self, duration_ms):
        for m in self.mobjects:
            m.update()
        self._timeline.append(([m.copy() for m in self.mobjects], duration_ms))

    # ── Rendering ──────────────────────────────────────────────────────
    def build(self):
        if not self._built:
            self.setup()
            self.construct()
            if not self._timeline:
                self._capture(self.theme.hold_ms)
            self._built = True
        return self

    @property
    def n_frames(self):
        return len(self.build()._timeline)

    def frames(self, dpi=None, check_overlaps=True):
        """Yield ``(PIL.Image, duration_ms)`` for every recorded frame."""
        self.build()
        renderer = FrameRenderer(self.theme, dpi)
        report = self.overlap_report = OverlapReport()
        last = len(self._timeline) - 1
        for i, (snapshot, ms) in enumerate(self._timeline):
            ctx = renderer.draw(snapshot)
            if check_overlaps:
                check_frame(ctx, renderer.renderer, i, report)
            yield renderer.image(), (self.theme.final_hold_ms if i == last else ms)

    def render_gif(self, path=None, dpi=None, check_overlaps=True, strict=False):
        """Render every frame to a GIF (loop and final hold from the theme).

        ``dpi`` lowers resolution for quick drafts (e.g. ``dpi=50``).
        Overlapping labels are reported as warnings, or raise if ``strict``.
        """
        path = self._out_path(path, ".gif")
        self.build()
        durations = [ms for _, ms in self._timeline]
        durations[-1] = self.theme.final_hold_ms
        images = (img for img, _ in self.frames(dpi, check_overlaps))
        first = next(images)
        # Pillow pulls the rest lazily, so only a couple of frames are in memory.
        first.save(path, save_all=True, append_images=images,
                   duration=durations, loop=self.theme.gif_loop, optimize=True)
        self._report_overlaps(strict)
        print(f"Saved {path} ({len(durations)} frames)")
        return path

    def render_png(self, path=None, frame=-1, dpi=None, check_overlaps=True, strict=False):
        """Render a single frame (default: the last) to PNG."""
        self.build()
        path = self._out_path(path, ".png")
        snapshot, _ = self._timeline[frame]
        renderer = FrameRenderer(self.theme, dpi)
        ctx = renderer.draw(snapshot)
        report = OverlapReport()
        if check_overlaps:
            check_frame(ctx, renderer.renderer, frame % len(self._timeline), report)
        self.overlap_report = report
        renderer.image().save(path)
        self._report_overlaps(strict)
        print(f"Saved {path}")
        return path

    def render_frames(self, out_dir, dpi=None):
        """Write every frame as a numbered PNG (useful for review)."""
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        for i, (img, _) in enumerate(self.frames(dpi)):
            p = os.path.join(out_dir, f"frame_{i:03d}.png")
            img.save(p)
            paths.append(p)
        self._report_overlaps(False)
        return paths

    def _out_path(self, path, ext):
        if path is None:
            name = re.sub(r"(?<!^)(?=[A-Z])", "_", type(self).__name__).lower()
            path = name + ext
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        return path

    def _report_overlaps(self, strict):
        r = self.overlap_report
        if not r:
            return
        msg = f"{type(self).__name__}: overlapping labels\n{r}"
        if strict:
            raise OverlapError(msg)
        warnings.warn(msg, stacklevel=3)
