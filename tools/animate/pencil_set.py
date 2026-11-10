#!/usr/bin/env python3
"""Pencil-style character sets (owner 2026-11-10: the new drawing style next to the 3D one — the 3D sets stay).

Run with the ComfyUI venv (numpy + OpenCV):  V=/media/msn/GamesLinux/AI/ComfyUI/venv/bin/python
    $V tools/animate/pencil_set.py like still-rgba.png frame.png out.png
        a mouth frame cut with the still's own outline and paper level (so edges never flicker between frames).
    $V tools/animate/pencil_set.py cutout in.png out.png [--green out-green.png]
        the drawing lifted off its white paper → RGBA (lines, colour and enclosed white parts stay; the paper, its
        grey tone and loose floor lines go). --green also writes it on flat chroma green (#00B140) for green-screen use.
"""
import sys, pathlib
import numpy as np, cv2

GREEN = (0, 177, 64)


def cutout(src, dst, green=None):
    im = cv2.imread(str(src), cv2.IMREAD_COLOR)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.GaussianBlur(cv2.dilate(g, np.ones((61, 61), np.uint8)), (0, 0), 20)   # paper level, also behind dark clothes
    flat = np.clip(g / np.maximum(bg, 1) * 255, 0, 255)               # paper → ~255 everywhere
    sat = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 1]
    ink = ((flat < 228) | (sat > 30)).astype(np.uint8)                # lines, shading or any colour
    H = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((1, 121), np.uint8))          # long horizontal runs …
    ink = ink & (1 - (H & (1 - cv2.morphologyEx(H, cv2.MORPH_OPEN, np.ones((9, 1), np.uint8)))))   # … that are thin = a floor line
    # floor shadow (2026-11-10): near the feet only strong lines count, the light grey hatching under the shoes goes
    ys = np.where(ink.any(axis=1))[0]
    if len(ys):
        cut = int(ys[-1] - 0.07 * (ys[-1] - ys[0]))
        strong = ((flat < 165) | (sat > 45)).astype(np.uint8)
        ink[cut:] = strong[cut:]
    # the outer outline: close gaps up to ~15 px, then everything inside it is the person (white shirts, necks,
    # blouses included); only paper that reaches the picture's edge goes (2026-11-10: a neck gap showed green)
    closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab = cv2.connectedComponents((1 - closed).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    paper = np.isin(lab, list(border)).astype(np.uint8)
    body = 1 - paper
    n, lab, st, _ = cv2.connectedComponentsWithStats(body, connectivity=8)  # keep the person, drop loose lines/specks
    if n > 1:
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep = (lab == big)
        for i in range(1, n):                                        # small pieces close to the person stay (fingers, hair)
            if i != big and st[i, cv2.CC_STAT_AREA] > 400 and st[i, cv2.CC_STAT_WIDTH] < im.shape[1] * 0.5:
                keep |= lab == i
        body = keep.astype(np.uint8)
    alpha = cv2.GaussianBlur(body.astype(np.float32) * 255, (3, 3), 0).astype(np.uint8)
    lvl = np.percentile(im[paper > 0], 60, axis=0) if paper.any() else np.array([255, 255, 255])
    rgb = np.clip(im.astype(np.float32) * 255 / np.maximum(lvl, 1), 0, 255).astype(np.uint8)   # one paper→white scale, colours keep their tone
    out = np.dstack([rgb, alpha])
    cv2.imwrite(str(dst), out)
    if green:
        a = alpha[..., None].astype(np.float32) / 255
        gr = np.zeros_like(im, dtype=np.float32); gr[:] = GREEN[::-1]
        cv2.imwrite(str(green), (rgb * a + gr * (1 - a)).astype(np.uint8))


def like(still, frame, dst):
    st = cv2.imread(str(still), cv2.IMREAD_UNCHANGED); im = cv2.imread(str(frame), cv2.IMREAD_COLOR)
    src = cv2.imread(str(still).replace("/sets/pencil/", "/work/pencil-sets/"), cv2.IMREAD_COLOR)   # the still before levelling
    lvl = np.percentile(src[st[..., 3] < 10], 60, axis=0) if src is not None else np.array([235, 235, 235])
    rgb = np.clip(im.astype(np.float32) * 255 / np.maximum(lvl, 1), 0, 255).astype(np.uint8)
    cv2.imwrite(str(dst), np.dstack([rgb, st[..., 3]]))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cutout":
        gr = sys.argv[sys.argv.index("--green") + 1] if "--green" in sys.argv else None
        cutout(sys.argv[2], sys.argv[3], gr)
    elif cmd == "like":
        like(sys.argv[2], sys.argv[3], sys.argv[4])
