#!/usr/bin/env python3
"""The 3D-film narrator (library/work/narrator/film3d/base.png, green screen) cut out cleanly, for the channel logo
and banner (owner 2026-11-04). Returns an RGBA image; the green fringe is removed (alpha eroded + despilled)."""
import pathlib
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def cutout():
    a = np.asarray(Image.open(ROOT / "library/work/narrator/film3d/base.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    alpha = Image.fromarray(np.clip(255 - ((g - np.maximum(r, b)) - 20) * 8, 0, 255).astype("uint8"))
    alpha = alpha.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))   # pull the edge in 2 px
    a[..., 1] = np.minimum(g, np.maximum(r, b))                                             # no green left in the rim
    return Image.merge("RGBA", (*Image.fromarray(a.astype("uint8")).split(), alpha))


def terracotta(w, h, seed=7):
    """The clay logo's background: darker bottom-left → lighter top-right, a soft clay grain."""
    yy, xx = np.mgrid[0:h, 0:w]; t = np.clip((xx / w + (1 - yy / h)) / 2, 0, 1)[..., None]
    lo, hi = np.array([160, 88, 44]), np.array([198, 122, 76])
    bg = lo + (hi - lo) * (0.35 + 0.65 * t) + np.random.default_rng(seed).normal(0, 1.4, (h, w, 1))
    return Image.fromarray(np.clip(bg, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.6))
