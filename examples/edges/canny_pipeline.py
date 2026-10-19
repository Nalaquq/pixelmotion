"""The whole Canny pipeline, one panel per step."""

from pixelmotion import *
from pixelmotion import data, edges


class CannyPipeline(Slide):
    title = "Canny Edge Detection"
    subtitle = "Blur → Gradient → Non-max suppression → Double threshold → Hysteresis"

    def construct(self):
        steps = edges.canny(data.shapes(96))
        pipeline = ImagePipeline(steps.stages(), self.main.inset(0.2), cols=3)
        self.play(Create(pipeline), run_time=6)
        self.wait(3)


if __name__ == "__main__":
    CannyPipeline().render_gif("out/canny_pipeline.gif")
