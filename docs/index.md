# pixelmotion

**Animated slides for math and computer vision, in the spirit of
[3Blue1Brown's manim](https://www.manim.community/), built on matplotlib.**

![Mean-centering a data matrix](assets/gallery/mean_centering.gif)

You describe *what happens*; pixelmotion renders the frames:

```python
from pixelmotion import *

class MeanCentering(Slide):
    title = "Step 1: Mean-Centering the Data"
    info = ["# Why centre?", "PCA finds directions of maximum variance."]

    def construct(self):
        X = Matrix([[150, 50], [170, 70], [190, 60]], label="$X$").move_to(self.main)
        self.play(FadeIn(X))
        self.play(X.animate.set_values([[-20, -10], [0, 10], [20, 0]]))  # numbers count
        self.wait()

MeanCentering().render_gif("mean_centering.gif")
```

## Why pixelmotion?

- **Objects for the things you teach.** Matrices, vectors, coordinate planes,
  pixel grids, kernels, convolution sweeps, gradients, and every step of
  Canny edge detection, with more domains on the way.
- **Real data stays easy.** It is matplotlib underneath, so real photos,
  plots, and 3D surfaces work out of the box.
- **Slides, not videos.** Output is GIF/PNG sized for PowerPoint (16:9,
  2400×1350), styled to a consistent course look. You choose how smooth the
  animation is when you render.
- **Catches layout bugs.** Every frame is checked for labels that collide
  with each other or sit on top of arrows, including mid-animation.

## Where to go next

<div class="grid cards" markdown>

- [**Getting started**](getting-started.md): install and render your first scene
- [**What you can draw**](draw/basics.md): every object, by topic, with live examples
- [**Building scenes**](guide/scenes.md): animations, layout, and rendering

</div>
