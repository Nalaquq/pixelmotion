# Slides & layout

`Slide` gives every scene the course look: a bold title, an italic subtitle,
an optional rounded info panel on the left, and named regions for content.

```text
┌──────────────────────────────────────────────────────────┐
│                      Title (30pt)                        │
│                    subtitle (italic)                     │
│ ┌─────────────┐  ┌─────────────────────────────────────┐ │
│ │ self.left   │  │ self.main (= self.right)            │ │
│ │ InfoPanel   │  │                                     │ │
│ └─────────────┘  └─────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

Without an `info` list, `self.main` spans the full content width.

## Info panel items

The panel wraps and stacks text for you, so there are no y-coordinates to tune:

```python
info = [
    "# Why centre?",                              # heading
    "PCA finds directions of maximum variance.",  # body (auto-wrapped)
    "",                                           # gap
    ("E(h) = 170 cm", GREEN),                     # bold, colored
    "~ Subtract these from every row.",           # subdued aside
]
```

Reveal items one at a time with
`self.play(LaggedStart(*[FadeIn(i) for i in self.info_panel.items]))`.
A warning is raised if the content overflows the box.

## Reference

::: pixelmotion.slide.Slide

::: pixelmotion.slide.InfoPanel

::: pixelmotion.slide.Region

::: pixelmotion.slide.Title
