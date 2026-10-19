# Linear algebra

Matrices whose numbers count smoothly to new values, vectors, and coordinate
planes that warp under a matrix, as in *Essence of Linear Algebra*.

## Matrices

![Mean-centering](../assets/gallery/mean_centering.gif)

??? example "Source: `examples/linalg/mean_centering.py`"
    ```python
    --8<-- "examples/linalg/mean_centering.py"
    ```

Things to know:

- **Numbers interpolate.** `Transform(A, B)` between numeric matrices of the
  same shape counts each entry from its old to its new value.
- **Symbols cross-fade.** Entries that are strings (`r"$h_1$"`) fade between
  versions.
- **Highlight** rows or columns with `highlight_row(i)` / `highlight_col(j)`,
  and animate it: `self.play(M.animate.highlight_row(1))`.
- **Labels** (`label`, `col_labels`, `row_labels`) are separate text
  objects, so renaming `X` to `X̃` doesn't interrupt the counting.

::: pixelmotion.linalg.Matrix

## Planes, vectors, and linear maps

![Linear transformation](../assets/gallery/linear_transform.gif)

??? example "Source: `examples/linalg/linear_transform.py`"
    ```python
    --8<-- "examples/linalg/linear_transform.py"
    ```

Anything added to a `Plane` uses plane coordinates and moves with it under
`ApplyMatrix`. A faint copy of the original grid stays behind for reference.
Use `plane.c2p(x, y)` to place canvas objects (like a matrix card) at a plane
point.

::: pixelmotion.linalg.Plane

::: pixelmotion.linalg.Vector

::: pixelmotion.linalg.ApplyMatrix
