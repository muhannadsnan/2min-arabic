#!/usr/bin/env python3
"""Render every on-screen card of a script into one sheet, BEFORE generating anything.

    python3 tools/check_cards.py videos/006-….md     → output/<video>/cards-sheet.png  (look at it)

Look for: empty boxes (□ = a glyph the font lacks), jumbled Arabic, text too small, NEW/answer lines highlighted.
Known traps: the Arabic font has no "…" or "_", the bold Latin font has no "→" or "▶".
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import assemble as A  # noqa: E402


def main():
    script = pathlib.Path(sys.argv[1])
    out = ROOT / "output" / script.stem / "cards-check"
    out.mkdir(parents=True, exist_ok=True)
    cards = []
    import re
    for i, text in enumerate(A.on_screen_by_scene(script), 1):
        if text:
            parts = [A.clean(x) for x in text.split(" · ")]
            for j, part in enumerate(parts):   # Arabic only renders in the FIRST part, without → … _
                ar = re.search(r"[\u0600-\u06ff]", part)
                if ar and (j > 0 or re.search(r"[A-Za-z]", part)):
                    print(f"⚠️ card {i}: Arabic outside the first part (renders as boxes): {part}")
                if ar and re.search(r"[→…_]", part):
                    print(f"⚠️ card {i}: → … or _ inside Arabic (missing glyph / wrong direction): {part}")
            p = out / f"c{i:02d}.png"
            A.render_card(text, p)
            cards.append(Image.open(p))
    W, cols = 1080, 3
    rows = (len(cards) + cols - 1) // cols
    ch = max(c.height for c in cards)
    sheet = Image.new("RGB", (W * cols, ch * rows), (90, 120, 140))
    for k, c in enumerate(cards):
        sheet.paste(c, ((k % cols) * W, (k // cols) * ch), c)
    target = ROOT / "output" / script.stem / "cards-sheet.png"
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(target)
    print(f"{len(cards)} cards → {target}")


if __name__ == "__main__":
    main()
