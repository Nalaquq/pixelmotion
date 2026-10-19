import warnings

import numpy as np

from pixelmotion import *
from pixelmotion import data, edges


def test_sobel_sees_vertical_edge_only_in_x():
    gx, gy = edges.sobel(data.step_edge(8, low=0, high=100, at=4))
    assert gx[3, 3] > 0 and gx[3, 4] > 0      # brighter to the right
    assert np.allclose(gx[:, :2], 0)
    assert np.allclose(gy, 0)


def test_nms_neighbors_follow_image_coordinates():
    # 45 deg in image coords points right and down the rows
    assert edges.nms_neighbors(5, 5, 45) == ((6, 6), (4, 4))
    assert edges.nms_neighbors(5, 5, 0) == ((5, 6), (5, 4))
    assert edges.nms_neighbors(5, 5, -90) == ((6, 5), (4, 5))


def test_nms_thins_vertical_edge_to_one_pixel():
    gx, gy = edges.sobel(data.step_edge(9))
    thin = edges.non_max_suppression(edges.gradient_magnitude(gx, gy),
                                     edges.gradient_direction(gx, gy))
    assert ((thin[1:-1] > 0).sum(axis=1) == 1).all()


def test_hysteresis_grows_chains_and_drops_isolated_weak():
    S, W = edges.STRONG, edges.WEAK
    labels = np.array([[S, W, W, 0, 0, W]])
    waves = edges.hysteresis_waves(labels)
    assert len(waves) == 3                       # input + two growth rings
    assert (waves[1][0, :3] == [S, S, W]).all()
    assert edges.hysteresis(labels).tolist() == [[True, True, True, False, False, False]]


def test_canny_returns_every_step():
    st = edges.canny(data.shapes(48))
    assert st.edges.dtype == bool and st.edges.any()
    assert [s[0] for s in st.stages()][0] == "Input"
    assert set(np.unique(st.labels)) <= {0, 1, 2}


def test_nms_animation_matches_algorithm():
    mag = np.array([[0, 5, 9, 4, 0]] * 4, float)
    angle = np.zeros_like(mag)

    class S(Scene):
        def construct(self):
            g = PixelGrid(mag)
            self.out = PixelGrid.empty(mag.shape)
            self.add(g, self.out)
            self.play(NonMaxSuppression(g, angle, self.out, time_per_cell=0.5))
    s = S().build()
    expected = edges.non_max_suppression(mag, angle)
    assert np.allclose(s.out.values[1:-1, 1:-1], expected[1:-1, 1:-1])


def test_hysteresis_animation_ends_without_weak_pixels():
    L = np.array([[2, 1, 0, 1]])

    class S(Scene):
        def construct(self):
            self.g = PixelGrid(L, cmap="labels", vmin=0, vmax=2)
            self.add(self.g)
            self.play(Hysteresis(self.g))
    s = S().build()
    assert s.g.values.tolist() == [[2, 2, 0, 0]]


def test_edge_profile_finds_subpixel_edge():
    for kind in ("step", "ramp"):
        p = EdgeProfile(data.edge_signal(32, kind, width=8), (0, 0, 8, 6))
        assert p.edge_position() == 15.5
        assert abs(p.zero_crossing() - 15.5) < 1e-9


class _Timed(Scene):
    def construct(self):
        d = Dot((2, 2))
        self.play(FadeIn(d), run_time=2)
        self.play(d.animate.shift(RIGHT), run_time=1)


def test_smoothness_changes_frames_not_duration():
    slide, fluid = _Timed().build(), _Timed().build(smoothness="fluid")
    assert (slide.n_frames, fluid.n_frames) == (6, 30)
    total = [sum(ms for _, ms in s._timeline) for s in (slide, fluid)]
    assert total[0] == total[1] == 3000


def test_info_panel_spreads_to_fill_box():
    region = Region(0, 0, 4, 7)
    items = ["# A", "one", "", "# B", "two"]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        spread = InfoPanel(items, region)
    top = InfoPanel(items, region, valign="top")
    last = lambda p: p.items[-1].bbox()[1]
    assert last(spread) < last(top) - 1.0          # content reaches further down
    # gaps are capped, so a short list is centered: equal space above and below
    above = region.top - spread.items[0].bbox()[3]
    below = last(spread) - region.bottom
    assert abs(above - below) < 0.25
