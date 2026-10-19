# Images

Two ways to show an image:

| | `PixelGrid` | `ImagePanel` |
|---|---|---|
| For | small arrays you want to *read* (≤ ~12×12) | real photos and full-size results |
| Shows values | yes, per cell, with auto contrast | no |
| Animates | cells fill in, values change, windows slide over it | cross-fades between images |

```python
grid = PixelGrid(img[:6, :6], cell=0.5, label="Input")
photo = ImagePanel("street.jpg", self.right, title="Original")
edges = ImagePanel(sobel(img), self.right, title="Edges")
self.play(FadeIn(photo))
self.play(Transform(photo, edges))     # cross-fade to the result
```

`PixelGrid.empty(shape)` makes a grid of blank cells (`NaN`), ready to be
filled by an operation such as [`Convolve`](filters.md).

::: pixelmotion.image.PixelGrid

::: pixelmotion.image.ImagePanel
