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

| Call | Frames |
|---|---|
| `self.play(anim)` | `run_time / frame_ms`, i.e. 2 s → 4 frames at 500 ms |
| `self.play(anim, run_time=4)` | 8 frames |
| `self.wait()` | one frame held for `hold_ms` (800 ms) |
| `self.wait(3)` | one frame held for 3 s |
| last frame | held for `final_hold_ms` (60 s) |

All of these come from the [`Theme`](#theme). To make smoother (but larger)
GIFs, lower `frame_ms`.

## Theme

```python
import dataclasses
from pixelmotion import DEFAULT_THEME

smooth = dataclasses.replace(DEFAULT_THEME, frame_ms=100)
MyScene(theme=smooth).render_gif("smooth.gif")
```

::: pixelmotion.theme.Theme

## Reference

::: pixelmotion.core.Scene
