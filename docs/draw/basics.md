# Text & shapes

The building blocks every other object is made of. All of them can be
positioned, grouped, faded, transformed, and recolored.

```python
title = Text("Gradient", size=24, weight="bold", color=ACCENT)
eq = Text(r"$\nabla f = (\partial_x f,\ \partial_y f)$", size=22)
Group(title, eq).arrange(DOWN, buff=0.3).move_to(self.main)

arrow = Arrow((3, 2), (6, 4), color=ORANGE)
box = SurroundingRectangle(eq)           # orange outline around a mobject
self.play(Write(title), Create(arrow))
self.play(Create(box))
```

!!! note "Math"
    Wrap math in `$...$`; it renders with matplotlib mathtext. Use real
    subscripts (`$x_1$`), never Unicode subscript characters.

## Text

::: pixelmotion.basics.Text

## Shapes

::: pixelmotion.basics.Dot

::: pixelmotion.basics.Line

::: pixelmotion.basics.Arrow

::: pixelmotion.basics.Rectangle

::: pixelmotion.basics.shapes.RoundedBox

::: pixelmotion.basics.shapes.SurroundingRectangle

::: pixelmotion.basics.shapes.BackgroundRectangle

::: pixelmotion.basics.Circle

::: pixelmotion.basics.Polygon

## Grouping

::: pixelmotion.core.Group
