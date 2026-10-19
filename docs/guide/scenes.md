# Scenes & rendering

## How a scene runs

1. `setup()` runs first (`Slide` adds its title and info panel here).
2. `construct()` runs your code. Each `play` and `wait` **records frames**;
   these are cheap snapshots of every object, not images.
3. `render_gif()` / `render_png()` / `render_frames()` turn the snapshots
   into pixels, checking each frame for [overlaps](overlaps.md).

Because recording and rendering are separate, you can render the same scene
at draft resolution (`dpi=50`) and final resolution without changing code.

## Timing

Durations are in **seconds** and don't depend on how smooth the GIF is:

| Call | Lasts |
|---|---|
| `self.play(anim)` | 2 s (the default `run_time`) |
| `self.play(anim, run_time=4)` | 4 s |
| `self.wait()` | 0.8 s (`hold_ms`) |
| `self.wait(3)` | 3 s |
| last frame | held 60 s (`final_hold_ms`) so the slide sits still |

## Smoothness

Choose how many frames fill that time when you render:

```python
scene.render_gif("slide.gif")                       # "slide": 500 ms frames (default)
scene.render_gif("smooth.gif", smoothness="smooth")  # 200 ms frames
scene.render_gif("fluid.gif", smoothness="fluid")    # 100 ms frames
scene.render_gif("custom.gif", smoothness=80)        # any frame length in ms
```

| Smoothness | Frame | Feel | Size |
|---|---|---|---|
| `"slide"` | 500 ms | stepped, deliberate; matches the course style guide | smallest |
| `"smooth"` | 200 ms | gentle motion | ~2.5× |
| `"fluid"` | 100 ms | video-like | ~5× |

The scene takes just as long at every setting; only the frame count changes.
Identical frames (holds, slow sweeps) are merged in the GIF, so the size grows
with the motion, not with the duration.

## Theme

Colors, font sizes, DPI, and timing defaults live in a `Theme`:

```python
import dataclasses
from pixelmotion import DEFAULT_THEME

web = dataclasses.replace(DEFAULT_THEME, gif_loop=0, final_hold_ms=3000)
MyScene(theme=web).render_gif("loops_forever.gif")
```

::: pixelmotion.theme.Theme

## Reference

::: pixelmotion.core.Scene
