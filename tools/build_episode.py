#!/usr/bin/env python3
"""Build a monthly Episode script from the month's Shorts (owner, 2026-10-24 — docs/21-monthly-episode.md).

    python3 tools/build_episode.py episodes/ep-01.json          # writes the script, prompts.json and map.json
    python3 tools/build_episode.py episodes/ep-01.json --check  # only lists narrator lines that still mention a day

episodes/ep-NN.json:
  {"stem": "ep01-…", "title": "…", "intro": [scene…], "chapters": [{"title": "…", "image": "ep01-fillers/s06.png",
   "line": "<narrator line that opens the chapter>", "items": [{"script": "002-…", "scenes": [3, 13]}, …]}, …],
   "rewrite": {"<old narrator/card text>": "<new text>", …}, "custom": {…}}
Every item copies the scenes a..b of that Short (lesson body only — no hook, intro, recall, "Your turn" or outro),
renumbered; pictures come from the Short's own images (images/<script>/sNN.png, "same" chains resolved) with the same
"shift"; Arabic lines keep the owner's/Koki's recordings (map.json from all recordings); narrator lines that mention a
day number, "yesterday" or "tomorrow" must be listed in "rewrite" (the build stops otherwise).
A chapter can also hold hand-written scenes: {"custom": [{"title": …, "image": "<video>/sNN.png", "card": …,
"say": [["narrator", "…"], ["sami", "…"]], "pause": 2}, …]}.
"""
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD = re.compile(r"^### 🎬 Scene (\d+) — (.+?)(?:\s+·\s+[\d:–-]+)?\s*$", re.M)
DAYREF = re.compile(r"\b[Dd]ay ?\d+|\byesterday\b|\btomorrow\b|\bnext lesson\b|\blast week\b|\bthis week\b|\bweek \d", re.I)


def scenes(md):
    out, heads = {}, list(HEAD.finditer(md))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(md)
        out[int(h.group(1))] = (h.group(2).strip(), md[h.end():end].strip("\n"))
    return out


def image_of(script, n, prompts):
    """The picture file + shift a scene of a Short used (follows "same" chains)."""
    by_s = {e["s"]: e for e in prompts if isinstance(e, dict) and "s" in e}
    shift, k, seen = None, n, set()
    while k in by_s and "same" in by_s[k] and k not in seen:
        seen.add(k); shift = by_s[k].get("shift", shift); k = by_s[k]["same"]
    e = by_s.get(k, {})
    if shift is None:
        shift = by_s.get(n, {}).get("shift", e.get("shift", 0))
    f = ROOT / "images" / script / f"s{k:02d}.png"
    return f"{script}/s{k:02d}.png", shift, f.exists()


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    check = "--check" in sys.argv
    rw = spec.get("rewrite", {})
    md = [f"# {spec['title']}", "", "Built by tools/build_episode.py from the month's Shorts (docs/21-monthly-episode.md) — "
          "no day numbers; Arabic = the owner's and Koki's recordings.", "", "---", ""]
    prompts, n, problems, missing_img = [{"style": "semi"}], 0, [], []
    chapters = []

    def add_scene(title, body, img, shift):
        nonlocal n
        n += 1
        md.extend([f"### 🎬 Scene {n} — {title}", "", body.strip(), ""])
        prompts.append({"s": n, "from": img, "shift": shift or 0})

    for e in spec.get("intro", []):
        add_scene(e["title"], f"🖼️ **Image:** {e['image']}\n🔤 **On screen:** {e['card']}\n\n```say:narrator\n{e['line']}\n```",
                  e["image"], e.get("shift", 0))
    for ci, ch in enumerate(spec["chapters"], 1):
        chapters.append({"title": ch["title"], "first_scene": n + 1})
        add_scene(f"Chapter {ci}: {ch['title']}",
                  f"🖼️ **Image:** {ch['image']}\n🔤 **On screen:** {ch.get('card', ch['title'])}\n\n```say:narrator\n{ch['line']}\n```",
                  ch["image"], ch.get("shift", 0))
        for it in ch.get("items", []):
            src = (ROOT / "videos").glob(f"{it['script']}.md")
            src = next(iter(sorted(src)), None)
            if not src:
                sys.exit(f"no script videos/{it['script']}.md")
            sc = scenes(src.read_text(encoding="utf-8"))
            pr = json.loads((ROOT / "images" / it["script"] / "prompts.json").read_text(encoding="utf-8"))
            a, b = it["scenes"]
            for k in range(a, b + 1):
                if k not in sc or k in it.get("skip", []):
                    continue
                title, body = sc[k]
                body = re.sub(r"^🖼️ \*\*Image:\*\*.*$", f"🖼️ **Image:** from {it['script']} scene {k}", body, flags=re.M)
                body = re.sub(r"^🎥 \*\*Clip:\*\*.*$", "", body, flags=re.M)
                for old, new in rw.items():
                    body = body.replace(old, new)
                for m in re.finditer(r"```say:narrator\n(.+?)\n```", body):
                    if DAYREF.search(m.group(1)) and not any(x in m.group(1) for x in spec.get("allow", [])):
                        problems.append(f"{it['script']} s{k}: {m.group(1)}")
                for m in re.finditer(r"^🔤 \*\*On screen:\*\*(.*)$", body, re.M):
                    if re.search(r"\bDay ?\d", m.group(1)):
                        problems.append(f"{it['script']} s{k} CARD: {m.group(1).strip()}")
                img, shift, ok = image_of(it["script"], k, pr)
                if not ok:
                    missing_img.append(img)
                add_scene(title, body, img, shift)
        for cs in ch.get("custom", []):
            lines = [f"🖼️ **Image:** {cs['image']}", f"🔤 **On screen:** {cs['card']}", ""]
            for sp, t in cs["say"]:
                lines += [f"```say:{sp}", t, "```"]
            if cs.get("pause"):
                lines.append(f"⏸️ **Pause {cs['pause']}s**")
            add_scene(cs["title"], "\n".join(lines), cs["image"], cs.get("shift", 0))
    for e in spec.get("outro", []):
        body = f"🖼️ **Image:** {e['image']}\n🔤 **On screen:** {e['card']}\n\n" + "\n".join(
            f"```say:{sp}\n{t}\n```" for sp, t in e["say"]) + ("\n🎥 **Clip:** goodbye — Thank you, and goodbye! (مع السلامة)" if e.get("goodbye") else "")
        add_scene(e["title"], body, e["image"], e.get("shift", 0))

    print(f"{n} scenes, {len(chapters)} chapters")
    if problems:
        print("narrator/card lines that still mention a day — add them to \"rewrite\":")
        print("\n".join("  " + p for p in problems))
    if missing_img:
        print("missing pictures:", missing_img)
    if check or problems or missing_img:
        sys.exit(1 if (problems or missing_img) and not check else 0)

    stem = spec["stem"]
    (ROOT / "videos" / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
    d = ROOT / "images" / stem; d.mkdir(parents=True, exist_ok=True)
    (d / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "chapters.json").write_text(json.dumps(chapters, ensure_ascii=False, indent=1), encoding="utf-8")
    pool = {}
    for f in sorted(glob.glob(str(ROOT / "footage/recordings/*/map.json"))):
        if "_placeholder" in f:
            continue
        for r in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            if r.get("file") and "_placeholder" not in r["file"]:
                pool.setdefault((r["speaker"], r["text"]), r)
    need = re.findall(r"```say:(teacher|teacher-slow|sami|lina|tom)\n(.+?)\n```", "\n".join(md))
    out, miss = [], []
    for i, (sp, t) in enumerate(need, 1):
        r = pool.get((sp, t))
        if r:
            out.append(dict(r, n=i))
        else:
            miss.append(f"[{sp}] {t}")
    rec = ROOT / "footage" / "recordings" / stem; rec.mkdir(parents=True, exist_ok=True)
    (rec / "map.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"videos/{stem}.md · images/{stem}/prompts.json · {len(out)} recorded lines mapped"
          + (f" · NOT recorded: {miss}" if miss else ""))


if __name__ == "__main__":
    main()
