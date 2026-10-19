# Overlap checker

Every rendered frame is checked for two common slide bugs:

- **text/text**: two labels whose boxes intersect
- **text/line**: a label sitting on a `Line`, `Arrow`, or `Vector`

Labels that are mid-fade (opacity < 0.3) are ignored.

Problems are reported as one warning per scene, grouped by the frames they
appear in:

```text
MeanCentering: overlapping labels
[text/text] '170' overlaps '31' (frames 14-15, 2 frames)
[text/text] 'E(h)' overlaps 'weight' (frame 14, 1 frames)
```

This catches collisions that only happen **mid-animation**, which are easy
to miss when you only look at the last frame.

## Options

```python
scene.render_gif("x.gif", strict=True)            # raise OverlapError instead
scene.render_gif("x.gif", check_overlaps=False)   # skip the check
scene.overlap_report.issues                       # inspect programmatically
```

## Common fixes

- **A label collides mid-animation**: delay it until the motion finishes
  (`Vector` labels do this automatically), or move objects in place instead
  of across others.
- **An old label stays under its replacement**: `FadeOut` the old one in the
  same `play` call as the new one.
- **A label sits on its arrow**: increase `label_buff`, or flip `label_side`.
