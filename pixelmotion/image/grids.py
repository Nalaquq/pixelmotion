"""Images as pixel grids (with values) and as full image panels."""

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import Normalize, to_rgba

from ..core.mobject import Mobject
from ..theme import DEFAULT_THEME, PANEL_BG, SUB, TEXT


class PixelGrid(Mobject):
    """A small image drawn as cells, optionally showing each pixel's value.

    Parameters
    ----------
    values : 2-D array
        Pixel values; ``NaN`` cells are drawn empty (handy for outputs that
        fill in during an animation).
    center : (x, y)
        Canvas position (default: canvas center).
    cell : float
        Cell size in canvas units (inches).
    cmap : str or None
        Matplotlib colormap for cell colors, or None for a flat ``fill``.
    vmin, vmax : float
        Color scale limits (default 0-255).
    show_values : bool
    fmt : str
        Format for values, e.g. ``"{:.0f}"`` or ``"{:.2f}"``.
    label : str, optional
        Caption above the grid.

    Notes
    -----
    ``Create`` fills the cells in reading order.
    """

    def __init__(self, values, center=None, cell=0.5, cmap="gray", vmin=0, vmax=255,
                 show_values=True, fmt="{:.0f}", value_size=None, fill=PANEL_BG,
                 grid_color="#888888", border_color=TEXT, label=None, label_color=TEXT,
                 **kwargs):
        super().__init__(**kwargs)
        self.values = np.array(values, float)
        th = DEFAULT_THEME
        self.center = np.array(center if center is not None else (th.width / 2, th.height / 2),
                               float)
        self.cell = cell
        self.cmap = cmap
        self.vmin, self.vmax = vmin, vmax
        self.show_values = show_values
        self.fmt = fmt
        self.value_size = value_size if value_size is not None else cell * 72 * 0.34
        self.fill_color = fill
        self.grid_color = grid_color
        self.border_color = border_color
        self.label = label
        self.label_color = label_color

    @classmethod
    def empty(cls, shape, **kwargs):
        """A grid of ``shape`` with every cell blank (NaN)."""
        return cls(np.full(shape, np.nan), **kwargs)

    @property
    def shape(self):
        return self.values.shape

    def cell_center(self, r, c):
        h, w = self.shape
        return self.center + self.cell * np.array([c - (w - 1) / 2, (h - 1) / 2 - r])

    def cell_box(self, r, c, nrows=1, ncols=1):
        """(x0, y0, x1, y1) covering rows r..r+nrows-1 and cols c..c+ncols-1."""
        h, w = self.shape
        x0 = self.center[0] + (c - w / 2) * self.cell
        y1 = self.center[1] + (h / 2 - r) * self.cell
        return (x0, y1 - nrows * self.cell, x0 + ncols * self.cell, y1)

    def set_values(self, values):
        self.values = np.array(values, float).reshape(self.shape)
        return self

    def set_value(self, r, c, v):
        self.values = self.values.copy()
        self.values[r, c] = v
        return self

    def display_values(self):
        """Values printed in the cells (subclasses may differ from ``values``)."""
        return self.values

    def format_value(self, v):
        return self.fmt.format(v).replace("-", "−")

    def own_bbox(self):
        h, w = self.shape
        hw, hh = w * self.cell / 2, h * self.cell / 2
        cx, cy = self.center
        top = cy + hh + (0.45 if self.label else 0)
        return (cx - hw, cy - hh, cx + hw, top)

    def _shift_self(self, v):
        self.center = self.center + v

    def _rgba(self):
        h, w = self.shape
        if self.cmap is None:
            rgba = np.tile(to_rgba(self.fill_color), (h, w, 1))
        else:
            norm = Normalize(self.vmin, self.vmax, clip=True)
            rgba = colormaps[self.cmap](norm(np.nan_to_num(self.values)))
        rgba[np.isnan(self.values)] = to_rgba(PANEL_BG)
        return rgba

    def draw(self, ctx, alpha, progress):
        ax = ctx.ax
        h, w = self.shape
        x0, y0, x1, y1 = self.cell_box(0, 0, h, w)
        rgba = self._rgba()
        shown = int(np.ceil(progress * h * w - 1e-9))
        if shown < h * w:
            rgba = rgba.copy()
            rgba.reshape(-1, 4)[shown:] = to_rgba(PANEL_BG)
        ax.imshow(rgba, extent=(x0, x1, y0, y1), interpolation="nearest", alpha=alpha,
                  zorder=1, aspect="auto")
        gx = np.linspace(x0, x1, w + 1)
        gy = np.linspace(y0, y1, h + 1)
        ax.vlines(gx[1:-1], y0, y1, color=self.grid_color, lw=0.8, alpha=alpha, zorder=2)
        ax.hlines(gy[1:-1], x0, x1, color=self.grid_color, lw=0.8, alpha=alpha, zorder=2)
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color=self.border_color, lw=1.8,
                alpha=alpha, zorder=2)
        if self.show_values:
            shown_vals = self.display_values()
            for k in range(min(shown, h * w)):
                r, c = divmod(k, w)
                v = shown_vals[r, c]
                if np.isnan(v):
                    continue
                lum = np.dot(rgba[r, c, :3], [0.299, 0.587, 0.114])
                x, y = self.cell_center(r, c)
                ax.text(x, y, self.format_value(v),
                        fontsize=self.value_size, color="white" if lum < 0.5 else TEXT,
                        ha="center", va="center", alpha=alpha, zorder=3)
        if self.label:
            ax.text((x0 + x1) / 2, y1 + 0.22, self.label, fontsize=13, color=self.label_color,
                    weight="bold", ha="center", va="bottom", alpha=alpha)


class ImagePanel(Mobject):
    """A full image (array or file path) in its own panel.

    Parameters
    ----------
    image : array (H x W or H x W x 3/4) or str path
    rect : Region or (x, y, w, h)
        Canvas area; the image keeps its aspect ratio inside it.
    cmap : str, optional
        For single-channel images (default "gray").
    title : str, optional
        Caption above the image.

    Notes
    -----
    ``Transform`` between two panels of the same size cross-fades the images.
    """

    _no_copy = Mobject._no_copy + ("image",)

    def __init__(self, image, rect, cmap="gray", vmin=None, vmax=None, title=None,
                 title_color=TEXT, border=False, **kwargs):
        super().__init__(**kwargs)
        if isinstance(image, str):
            from PIL import Image
            image = np.asarray(Image.open(image))
        self.image = np.asarray(image)
        self.rect = np.array(getattr(rect, "rect", rect), float)
        self.cmap = cmap
        self.vmin, self.vmax = vmin, vmax
        self.title = title
        self.title_color = title_color
        self.border = border

    def own_bbox(self):
        x, y, w, h = self.rect
        return (x, y, x + w, y + h)

    def _shift_self(self, v):
        self.rect = self.rect + np.array([v[0], v[1], 0, 0])

    def draw(self, ctx, alpha, progress):
        ax = ctx.new_axes(tuple(self.rect))
        ax.imshow(self.image, cmap=self.cmap if self.image.ndim == 2 else None,
                  vmin=self.vmin, vmax=self.vmax, alpha=alpha * progress, interpolation="nearest")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(self.border)
            s.set_color(SUB)
        ax.patch.set_alpha(0)
        if self.title:
            ax.set_title(self.title, fontsize=14, color=self.title_color, weight="bold",
                         alpha=alpha, pad=8)
        ctx.ax = ctx.canvas
