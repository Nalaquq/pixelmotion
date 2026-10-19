# Filtering & convolution

Kernels and the sliding-window animation behind blur, sharpening, and edge
detection.

![Box blur](../assets/gallery/box_blur.gif)

??? example "Source: `examples/filters/box_blur.py`"
    ```python
    --8<-- "examples/filters/box_blur.py"
    ```

`Convolve` moves an orange window across the input, fills each output cell as
it goes, and shows the running sum. Pass `cells=[...]` to walk through a few
positions slowly (with a larger `time_per_cell`) before sweeping the rest.

!!! note "Correlation vs convolution"
    Like OpenCV and most CV texts, `Convolve` slides the kernel *as is*
    (cross-correlation). Pass `flip=True` for textbook convolution.

::: pixelmotion.filters.Kernel

::: pixelmotion.filters.Convolve

::: pixelmotion.filters.correlate_valid
