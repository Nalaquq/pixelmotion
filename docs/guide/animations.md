# Animations

| Animation | What it does |
|---|---|
| `FadeIn(m, shift=UP)` | fade in, optionally sliding in along `shift` |
| `FadeOut(m)` | fade out and remove |
| `Create(m)` | draw in: lines grow, grids fill, groups appear in order |
| `Write(text)` | type text on left to right |
| `Uncreate(m)` | reverse of `Create` |
| `Transform(a, b)` | morph `a` into `b` (numbers and colors interpolate) |
| `ReplacementTransform(a, b)` | morph, then put `b` in the scene in place of `a` |
| `Indicate(m)` | flash a highlight color and back |
| `m.animate.<methods>` | animate any change you can make with methods |

## `.animate`

Any method chain becomes an animation:

```python
self.play(dot.animate.shift(RIGHT * 2).set_color(RED))
self.play(M.animate(run_time=3).highlight_row(1))
self.play(plane.animate.apply_matrix([[0, -1], [1, 0]]))   # rotate 90°
```

## Playing several at once

```python
self.play(FadeIn(a), FadeIn(b))                  # together
self.play(FadeIn(a), FadeIn(b), lag_ratio=0.5)   # b starts halfway through a
self.play(LaggedStart(*[FadeIn(i) for i in panel.items]))
self.play(Succession(Create(x), Write(label)))   # one after another
```

## Easing

`rate_func` controls pacing: `smooth` (default), `linear`, `rush_into`,
`rush_from`, `there_and_back`, and `stepped(n)` from `pixelmotion.rate_functions`.

## Updaters and value trackers

To keep one object in sync with another, add an **updater**, a function
run before every frame:

```python
t = ValueTracker(0)
dot = Dot()
dot.add_updater(lambda d: d.move_to(plane.c2p(t.get_value(), t.get_value() ** 2)))
self.add(dot)
self.play(t.animate.set_value(2))    # the dot rides along y = x²
```

## How interpolation works

`Transform` compares the two objects attribute by attribute:

- numbers and arrays → linear interpolation
- attributes with `color` in the name → blended in RGB
- `True`/`False` flags → switch halfway
- child objects → matched pairwise and interpolated recursively
- anything else that differs (e.g. text) → that object cross-fades

So a matrix keeps counting while only its renamed label cross-fades.

## Reference

::: pixelmotion.animation.Transform

::: pixelmotion.animation.FadeIn

::: pixelmotion.animation.Create

::: pixelmotion.animation.Indicate

::: pixelmotion.animation.AnimationGroup

::: pixelmotion.animation.transform.AnimateBuilder

::: pixelmotion.core.ValueTracker
