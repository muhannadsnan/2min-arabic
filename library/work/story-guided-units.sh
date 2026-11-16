#!/bin/bash
# Story Shorts 2–5 with an English line before every Arabic line (owner 2026-11-16) — C2 narrator, then build
cd "$(dirname "$0")/../.." || exit 1
while pgrep -f "[s]teamapps/common" >/dev/null; do sleep 30; done
STEMS="${*:-s01-3-opposites s01-4-past s01-5-future}" python3 - <<'PY' 2>&1 | grep -E "^(u|h|ERR)"
import sys, json, pathlib, re, os, shutil
sys.path.insert(0, "tools"); import make_audio as M
P = json.load(open("videos/s01-shorts-guided.json", encoding="utf-8"))
def say(t): return re.sub(r"\bKamel\b", "Kamil", re.sub(r"\bMazen\b", "Mazin", re.sub(r"\bMaher\b", "Maahir", t))).replace("…", "...")
V = "narrator-c2c"   # owner 2026-11-17: "c2 70-30" (was C = narrator-dry on 16 Nov)
for stem in os.environ["STEMS"].split():
    v = P[stem]
    hf = pathlib.Path("audio/s01-hooks-c2c"); hf.mkdir(exist_ok=True)
    if not (hf / f"{stem}.json").exists(): shutil.copy(f"audio/s01-hooks-c2t/{stem}.json", hf / f"{stem}.json")
    ht = json.loads((hf / f"{stem}.json").read_text())["text"]
    for j in M.synthesize_missing({hf / f"{stem}.wav": (V, say(ht))}, hf, 6):
        print("h", stem[:6], "cer", round(j["cer"], 2), "|", j["heard"][:90], flush=True)
    folder = pathlib.Path(f"audio/s01-shorts-guided-c2c/{stem}"); folder.mkdir(parents=True, exist_ok=True)
    todo = {folder / f"u{k:02}.wav": (V, say(u.get("say", u["en"]))) for k, u in enumerate(v["units"], 1)}
    if v.get("outro"): todo[folder / "outro.wav"] = (V, say(v["outro"].get("say", v["outro"]["en"])))
    for j in sorted(M.synthesize_missing(todo, folder, 6), key=lambda j: j["cache"]):
        print("u", stem[:6], pathlib.Path(j["cache"]).stem, "cer", round(j["cer"], 2), "|", j["heard"][:90], flush=True)
PY
echo TTS_DONE
for s in ${@:-s01-3-opposites s01-4-past s01-5-future}; do
  timeout 900 python3 library/work/story-guided-units.py $s || echo "BUILD_FAIL $s"
done
echo UNITS_DONE $(date +%H:%M)
