import numpy as np
import pytest
from PIL import Image

from pixelmotion import *
from pixelmotion.core.mobject import interpolate_mobject
from pixelmotion.filters import correlate_valid


def test_numbers_and_colors_interpolate():
    a = Dot((0, 0), color="#000000")
    b = Dot((2, 4), color="#FFFFFF")
    mid = interpolate_mobject(a, b, 0.5)
    assert np.allclose(mid.point, (1, 2))
    assert mid.color.lower() == "#808080"
    assert mid._crossfade is None


def test_different_text_crossfades():
    mid = interpolate_mobject(Text("a"), Text("b"), 0.3)
    start, end, alpha, own_only = mid._crossfade
    assert (start.text, end.text, alpha, own_only) == ("a", "b", 0.3, False)


def test_panel_image_blends_while_title_interpolates_separately():
    a = ImagePanel(np.zeros((4, 4)), (0, 0, 4, 4), title="before")
    b = ImagePanel(np.ones((4, 4)), (0, 0, 4, 4), title="after")
    mid = interpolate_mobject(a, b, 0.5)
    assert mid._crossfade[3] is True                    # own image cross-fades
    assert mid.title._crossfade[0].text == "before"     # title handled on its own


def test_matrix_label_change_keeps_entries_interpolating():
    a = Matrix([[0, 10]], label="$X$")
    b = Matrix([[10, 20]], label=r"$\tilde{X}$")
    mid = interpolate_mobject(a, b, 0.5)
    assert mid._crossfade is None
    assert np.allclose(mid.values, [[5, 15]])
    assert mid.get_label()._crossfade is not None


def test_become_preserves_child_identity():
    child = Text("x")
    g = Group(child, Text("y"))
    g.become(g.copy().shift(RIGHT))
    assert g[0] is child
    assert np.allclose(child.pos, np.array([DEFAULT_THEME.width / 2 + 1, DEFAULT_THEME.height / 2]))


def test_next_to_places_beside_and_centers():
    a = Rectangle(2, 2, center=(5, 5))
    b = Rectangle(1, 1, center=(0, 0)).next_to(a, RIGHT, buff=0.5)
    assert np.allclose(b.get_center(), (6.0 + 0.5 + 0.5, 5))


def test_matrix_formatting():
    m = Matrix([[-20, 0, 10]], signed=True)
    assert [m.entry_text(0, j) for j in range(3)] == ["−20", "0", "+10"]


def test_correlate_matches_manual():
    img = np.arange(16.0).reshape(4, 4)
    k = np.ones((3, 3)) / 9
    out = correlate_valid(img, k)
    assert out.shape == (2, 2)
    assert np.isclose(out[0, 0], img[:3, :3].mean())


class _Overlap(Scene):
    def construct(self):
        self.add(Text("HELLO", pos=(8, 4.5), size=30), Text("WORLD", pos=(8.2, 4.5), size=30))


class _LabelOnLine(Scene):
    def construct(self):
        self.add(Line((2, 4.5), (14, 4.5), name="axis"), Text("on the line", pos=(8, 4.5)))


class _Clean(Scene):
    def construct(self):
        self.add(Text("left", pos=(3, 4.5)), Text("right", pos=(13, 4.5)))


def test_overlap_checker_flags_text_collisions(tmp_path):
    s = _Overlap()
    with pytest.warns(UserWarning, match="overlapping labels"):
        s.render_png(tmp_path / "o.png", dpi=30)
    assert s.overlap_report.issues[0].kind == "text/text"


def test_overlap_checker_flags_label_on_line(tmp_path):
    s = _LabelOnLine()
    with pytest.raises(OverlapError):
        s.render_png(tmp_path / "l.png", dpi=30, strict=True)


def test_clean_scene_has_no_issues(tmp_path):
    s = _Clean()
    s.render_png(tmp_path / "c.png", dpi=30)
    assert not s.overlap_report


class _Anim(Scene):
    def construct(self):
        d = Dot((2, 2))
        self.play(FadeIn(d), run_time=1)
        self.play(d.animate.shift(RIGHT * 3), run_time=1)
        self.wait(1)


def test_gif_frames_and_timing(tmp_path):
    path = _Anim().render_gif(str(tmp_path / "a.gif"), dpi=20)
    with Image.open(path) as im:
        # 2 + 2 frames at 500 ms; Pillow merges the identical hold into the last one
        assert im.n_frames == 4
        im.seek(im.n_frames - 1)
        assert im.info["duration"] >= DEFAULT_THEME.final_hold_ms
        assert im.info.get("loop") == 1


def test_convolve_fills_output():
    class S(Scene):
        def construct(self):
            img = PixelGrid(np.arange(25.0).reshape(5, 5))
            k = Kernel(np.ones((3, 3)), scale="1/9")
            self.out = PixelGrid.empty((3, 3))
            self.add(img, k, self.out)
            self.play(Convolve(img, k, self.out))
    s = S().build()
    assert np.allclose(s.out.values, correlate_valid(np.arange(25.0).reshape(5, 5),
                                                     np.ones((3, 3)) / 9))
    assert s.n_frames == 9
