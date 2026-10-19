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

Two display options help with processed images:

- `ImagePanel(gx, rect, signed=True)` uses a red/blue scale centered on zero,
  for results with negative values (Sobel, Laplacian, DoG).
- `cmap="labels"` colors 0 / 1 / 2 as black / orange / white, for label
  maps such as Canny's none / weak / strong. `PixelGrid(...,
  value_labels={1: "W", 2: "S"})` prints letters instead of numbers.

::: pixelmotion.image.PixelGrid

::: pixelmotion.image.ImagePanel

## Pipelines

`ImagePipeline` lays out one panel per step of an algorithm, with arrows
between them. `Create` reveals the steps in order. See the
[Canny example](edges.md#the-whole-canny-pipeline).

::: pixelmotion.image.ImagePipeline

## Sample images

`pixelmotion.data` generates test images, so there is nothing to download
or license:

| Function | What you get |
|---|---|
| `data.shapes(size)` | rectangle, disk, triangle, and a faint ellipse on a gradient, with noise |
| `data.step_edge(size)` | one straight dark/bright edge |
| `data.edge_signal(n, kind)` | a 1-D row across a `"step"`, `"ramp"` (blurry), or `"line"` |
