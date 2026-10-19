# Edges

Everything for teaching edge detection, from "an edge is a rapid change" to
the full Canny pipeline. The objects draw the ideas; the algorithms in
`pixelmotion.edges` (plain NumPy) produce the images they show.

```python
from pixelmotion import *
from pixelmotion import data, edges
```

## Edges are rapid changes

![Edge profile](../assets/gallery/edge_profile.gif)

`EdgeProfile` plots one row of pixels with its first and second derivatives.
The pixels themselves sit on top, lined up with the plots. The edge is
marked where the first derivative peaks and the second crosses zero.
`Transform` to a blurrier signal shows the peak getting lower and wider.

??? example "Source: `examples/edges/edge_profile.py`"
    ```python
    --8<-- "examples/edges/edge_profile.py"
    ```

::: pixelmotion.edges.EdgeProfile

## Sobel filters

![Sobel X](../assets/gallery/sobel.gif)

Sobel is a convolution, so it reuses [`Kernel` and `Convolve`](filters.md)
with the kernels `edges.SOBEL_X` and `edges.SOBEL_Y`. Give the output grid a
diverging colormap (`cmap="RdBu_r"`, symmetric `vmin`/`vmax`) so sign reads
as color.

??? example "Source: `examples/edges/sobel.py`"
    ```python
    --8<-- "examples/edges/sobel.py"
    ```

## The gradient

![Gradient field](../assets/gallery/gradient_field.gif)

`GradientField` draws an arrow per pixel (every `step` pixels) over an image.
`GradientDiagram` zooms in on one pixel: Gx, then Gy, then the gradient
vector, with its strength and angle.

??? example "Source: `examples/edges/gradient_field.py`"
    ```python
    --8<-- "examples/edges/gradient_field.py"
    ```

!!! note "Image coordinates"
    Rows grow downward, so a positive Gy points *down*. Arrows, diagrams, and
    `edges.gradient_direction` all use this convention, so they agree with
    each other and with the picture.

::: pixelmotion.edges.GradientField

::: pixelmotion.edges.GradientDiagram

## Non-maximum suppression

![Non-max suppression](../assets/gallery/nms.gif)

`NonMaxSuppression` walks over a magnitude grid. For each pixel it shows the
two neighbors along the gradient and fills the output with the pixel's value
(keep) or 0 (suppress). A readout under the output says why.

??? example "Source: `examples/edges/nms.py`"
    ```python
    --8<-- "examples/edges/nms.py"
    ```

::: pixelmotion.edges.NonMaxSuppression

## Hysteresis

![Hysteresis](../assets/gallery/hysteresis.gif)

Draw thresholded pixels as a `PixelGrid` with `cmap="labels"` (0 = none,
1 = weak, 2 = strong). `Hysteresis` grows strong edges into touching weak
pixels one ring per step, then drops the weak pixels that never connected.

??? example "Source: `examples/edges/hysteresis.py`"
    ```python
    --8<-- "examples/edges/hysteresis.py"
    ```

::: pixelmotion.edges.Hysteresis

## The whole Canny pipeline

![Canny pipeline](../assets/gallery/canny_pipeline.gif)

`edges.canny(img)` keeps every intermediate image; `steps.stages()` hands
them straight to an [`ImagePipeline`](image.md#pipelines).

```python
steps = edges.canny(data.shapes(96))       # sigma, low, high are adjustable
self.play(Create(ImagePipeline(steps.stages(), self.main, cols=3)), run_time=6)
```

## Algorithms

All take and return NumPy arrays. They are written for clarity, which is
fine for slide-sized images.

::: pixelmotion.edges.canny

::: pixelmotion.edges.ops.CannySteps

::: pixelmotion.edges.sobel

::: pixelmotion.edges.gradient_magnitude

::: pixelmotion.edges.gradient_direction

::: pixelmotion.edges.non_max_suppression

::: pixelmotion.edges.nms_neighbors

::: pixelmotion.edges.double_threshold

::: pixelmotion.edges.hysteresis_waves

::: pixelmotion.edges.hysteresis

::: pixelmotion.edges.gaussian_kernel

::: pixelmotion.edges.gaussian_blur

::: pixelmotion.edges.laplacian

::: pixelmotion.edges.difference_of_gaussians

::: pixelmotion.edges.filter2d

Kernels: `SOBEL_X`, `SOBEL_Y`, `PREWITT_X`, `PREWITT_Y`, `LAPLACIAN`.
Label values: `NONE = 0`, `WEAK = 1`, `STRONG = 2`.
