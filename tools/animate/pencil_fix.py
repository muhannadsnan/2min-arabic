#!/usr/bin/env python3
"""Repairs for pencil talking sets (2026-11-10) — no generation, just careful pasting.

    python3 tools/animate/pencil_fix.py rebase new-still.png old-frame.png x0 y0 x1 y1 out.png
        a mouth frame moved onto an edited still (e.g. new eyes): only the mouth ellipse comes from the old frame,
        so every frame matches the new still everywhere else.
    python3 tools/animate/pencil_fix.py transplant face-frame.png fx0 fy0 fx1 fy1 target-still.png tx0 ty0 tx1 ty1 out.png
        the mouth area of a big face-shot frame, shrunk to the target's mouth box and pasted in with a soft edge — for
        shots where the face is too small to draw a mouth (the narrator's upper shot: crooked mouths in his beard).
Boxes are the mouth boxes of library/work/pencil-boxes.txt (corners of the smile).
"""
import sys
from PIL import Image, ImageDraw, ImageFilter


def ellipse_mask(size, box, grow_x, grow_y, blur):
    m = Image.new("L", size, 0); x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    ImageDraw.Draw(m).ellipse((x0 - grow_x * w, y0 - grow_y * h, x1 + grow_x * w, y1 + grow_y * h), fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))


def rebase(still, frame, box, out):
    s = Image.open(still).convert("RGB"); f = Image.open(frame).convert("RGB")
    m = ellipse_mask(s.size, box, 0.2, 0.35, max(1.5, (box[2] - box[0]) / 40))
    s.paste(f, (0, 0), m); s.save(out)


def transplant(face, fbox, target, tbox, out):
    f = Image.open(face).convert("RGB"); t = Image.open(target).convert("RGB")
    k = (tbox[2] - tbox[0]) / (fbox[2] - fbox[0])
    fw, fh = fbox[2] - fbox[0], fbox[3] - fbox[1]
    crop = (fbox[0] - 0.25 * fw, fbox[1] - 0.15 * fh, fbox[2] + 0.25 * fw, fbox[3] + 0.7 * fh)   # moustache + mouth + under the lip only (no nose, no cheeks)
    piece = f.crop(tuple(map(round, crop)))
    piece = piece.resize((max(1, round(piece.width * k)), max(1, round(piece.height * k))), Image.LANCZOS)
    tcx = (tbox[0] + tbox[2]) / 2; fcx = (fbox[0] + fbox[2]) / 2
    x = round(tcx - (fcx - crop[0]) * k); y = round(tbox[1] - (fbox[1] - crop[1]) * k)
    m = Image.new("L", piece.size, 0)
    ImageDraw.Draw(m).ellipse((piece.width * 0.06, piece.height * 0.16, piece.width * 0.94, piece.height * 0.94), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(max(1.5, piece.width / 18)))
    t.paste(piece, (x, y), m); t.save(out)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "rebase":
        rebase(a[2], a[3], tuple(map(int, a[4:8])), a[8])
    elif a[1] == "transplant":
        transplant(a[2], tuple(map(int, a[3:7])), a[7], tuple(map(int, a[8:12])), a[12])
