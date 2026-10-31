#!/usr/bin/env python3
"""The owner's Facebook-groups helper page (owner 2026-10-31: "a file with all content, I just copy-paste"):
groups.html on gh-pages. Meta has no API for posting in groups (removed 2024), so the owner posts by hand.

  · English groups: Open the Reel (on the Page) → Share → Group → paste the text.
  · Other languages: the Page stays English-only (owner 2026-10-31), so their version is a FILE the owner uploads
    into the group (~/Downloads/fb-groups/, listed in data/fb-group-files.json) + the text to paste.

3 groups a day, by the calendar (any day, the same 3 on every device: no storage needed), plus yesterday's 3 to
catch up. Not more at once: sharing into many groups in one sitting gets "temporarily blocked from posting in groups".

    python3 tools/fb_groups_page.py           # writes /tmp/groups.html to look at
    python3 tools/fb_groups_page.py --push    # commits groups.html to gh-pages (GitHub: site-latest.yml)

English Reels come from the Facebook Page (only those posted after the app went Live, 30 Oct 2026).
"""
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = "2026-10-30T13:00:00+0000"   # Meta app switched to Live: Reels before this were visible to app roles only
START = "2026-11-01"                # day 0 of the rotation
# the owner's groups (2026-10-31); (name, language, members, type). Target 3–5 per language.
GROUPS = [   # the owner's final list, 31 Oct 2026 (Facebook "Share to a group"), joined as the Page
    ("Learn Arabic in English", "en", "561K", "busy"),
    ("Arabic is very easy", "en", "395K", "busy"),
    ("Arabic Language Learners", "en", "236K", "busy"),
    ("Let's Learn Arabic", "en", "152K", "busy"),
    ("Learn Arabic & English", "en", "152K", "busy"),
    ("Learn how to speak Arabic language", "en", "123K", "busy"),
    ("Learn Arabic and other Languages", "en", "1.1M", "medium"),
    ("Learning simple arabic for beginners", "en", "42K", "busy"),
    ("Learn Arabic Easy", "en", "34K", "busy"),
    ("learn Arabic with English", "en", "27K", "busy"),
    ("Arabic Learning in English and Urdu", "ur", "340K", "quiet, admin approval — Urdu/English/Arabic only"),
    ("[ARABIC WORDS and their meanings in Urdu]", "ur", "17K", "quiet"),
    ("Learn URDU ARABIC,ENGLISH Online", "ur", "10K", "quiet"),
    ("Arabic - Urdu. عربی - اردو", "ur", "9.6K", "quiet"),
    ("Arabic English Lessons (Atik Sir)", "hi", "38K", "busy"),
    ("Belajar Bahasa Arab", "id", "109K", "medium"),
    ("Komunitas belajar bahasa arab", "id", "52K", "busy"),
    ("PERCAKAPAN BAHASA ARAB SEHARI-HARI", "id", "19K", "medium · everyday conversation = our content"),
    ("pembelajaran bahasa Arab dasar sehari_hari (PBA)", "id", "17K", "busy"),
    ("BELAJAR BAHASA ARAB (PEMULA)", "id", "12K", "quiet"),
    ("Arapça Dersi", "tr", "139K", "quiet"),
    ("Arapça Ders Öğren İrap Tahlil Cümle", "tr", "37K", "busy"),
    ("Arapça Öğrenmek İsteyenler", "tr", "11K", "quiet"),
]
LANG = {"en": "English", "ur": "Urdu", "hi": "Hindi", "id": "Indonesian", "tr": "Turkish", "ms": "Malay"}
CLOSE = {
    "en": "I'm a native Syrian Arabic speaker and post a 2-minute lesson every day. Questions welcome 🙂",
    "ur": "میں شام (سیریا) سے ہوں اور روز 2 منٹ کا عربی سبق بناتا ہوں۔ کوئی سوال ہو تو ضرور پوچھیں 🙂",
    "hi": "Main Syria se hoon aur roz 2 minute ka Arabic lesson banata hoon. Koi sawal ho to zaroor poochhein 🙂",
    "id": "Saya penutur asli bahasa Arab dari Suriah dan membuat pelajaran 2 menit setiap hari. Silakan bertanya 🙂",
    "ms": "Saya penutur asli bahasa Arab dari Syria dan membuat pelajaran 2 minit setiap hari. Silakan bertanya 🙂",
    "tr": "Suriyeliyim, ana dilim Arapça. Her gün 2 dakikalık bir ders paylaşıyorum. Sorularınızı bekliyorum 🙂",
}


def order():
    """Rotation: each language's groups spread evenly over the round (English has 10 of 23), so a day rarely gets
    the same language twice."""
    by = {}
    for i, g in enumerate(GROUPS):
        by.setdefault(g[1], []).append(i)
    slots = [((k + 0.5) / len(ids), -len(ids), i) for ids in by.values() for k, i in enumerate(ids)]
    return [i for *_, i in sorted(slots)]


def creds():
    if os.environ.get("FB_PAGE_TOKEN"):
        return os.environ["FB_PAGE_TOKEN"]
    return json.loads((pathlib.Path.home() / ".config/2min-facebook/page.json").read_text())["page_token"]


def reels():
    q = urllib.parse.urlencode({"fields": "id,created_time,description,permalink_url", "limit": 40, "access_token": creds()})
    with urllib.request.urlopen(f"https://graph.facebook.com/v21.0/me/video_reels?{q}", timeout=60) as r:
        data = json.load(r)["data"]
    return [v for v in data if v["created_time"] > LIVE and v.get("description")]


def is_english(caption):
    first = caption.strip().splitlines()[0]
    return not re.search(r"[؀-ۿऀ-ॿ]|Arapça|bahasa Arab|tiada|minit", first, re.I)


def paste_text(caption, lang):
    """The lesson part of the caption + a friendly line; drops hashtags, other-language lines and 'link in bio'."""
    keep = [p for p in caption.strip().split("\n\n")
            if not re.search(r"#|🌍|link|bio|लिंक|لنک|profil|YouTube", p, re.I)]
    tail = [CLOSE[lang]] + ([] if lang == "en" else ["▶️ YouTube: 2 Minute Arabic"])
    return "\n\n".join(keep + tail)


def content():
    en = [v for v in sorted(reels(), key=lambda v: v["created_time"], reverse=True) if is_english(v["description"])]
    files = json.loads((ROOT / "data" / "fb-group-files.json").read_text(encoding="utf-8"))
    return {
        "en": [{"url": "https://www.facebook.com" + v["permalink_url"], "title": v["description"].splitlines()[0][:90],
                "text": paste_text(v["description"], "en")} for v in en[:12]],
        "files": {l: {"file": f["file"], "title": f["video"], "text": paste_text(f["caption"], l)} for l, f in files.items()},
    }


def page(groups, rotation, data):
    blob = json.dumps({"groups": groups, "order": rotation, "start": START, **data}, ensure_ascii=False).replace("</", "<\\/")
    built = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %H:%M UTC")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Group posts</title><link rel="icon" href="favicon.png">
<style>
:root{{--bg:#fbf6ee;--card:#fff;--ink:#2a2420;--soft:#6f6258;--teal:#1f6f6b;--terra:#c8643b;--line:#eadfce}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1a17;--card:#27231f;--ink:#f3ece3;--soft:#b9ab9c;--line:#3a332c;--teal:#5fb3ad;--terra:#e08a63}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:640px;margin:0 auto;padding:20px 16px 48px}}
h1{{font-size:1.5rem;margin:0 0 4px}} h2{{font-size:1.1rem;margin:26px 0 10px}} .sub{{color:var(--soft);margin:0 0 18px}}
.steps{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:18px;color:var(--soft);font-size:.95rem}}
.steps b{{color:var(--ink)}} .steps p{{margin:4px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}}
.card.done{{opacity:.55}}
.top{{display:flex;gap:10px;align-items:flex-start;justify-content:space-between}}
.num{{background:var(--terra);color:#fff;border-radius:50%;width:30px;height:30px;display:grid;place-items:center;font-weight:700;flex:none}}
.g{{font-weight:700;font-size:1.08rem}} .meta{{color:var(--soft);font-size:.88rem}}
.lang{{display:inline-block;background:var(--teal);color:#fff;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:600;margin-right:6px}}
.btns{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px;align-items:center}}
a.btn,button{{font:inherit;font-weight:600;border-radius:10px;padding:10px 14px;border:0;cursor:pointer;text-decoration:none}}
a.btn{{background:var(--teal);color:#fff}} button.copy{{background:var(--terra);color:#fff}}
.file{{background:var(--bg);border:1px dashed var(--teal);border-radius:10px;padding:8px 12px;font-size:.93rem}}
.file b{{font-family:ui-monospace,monospace}}
pre{{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px;margin:0;font:inherit;font-size:.93rem;max-height:220px;overflow:auto}}
label{{display:flex;gap:8px;align-items:center;margin-top:10px;font-weight:600}} input{{width:20px;height:20px}}
.none{{color:var(--soft);font-style:italic}}
details{{margin-top:26px}} summary{{cursor:pointer;font-weight:700}}
table{{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:10px}} td,th{{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left;vertical-align:top}}
.foot{{color:var(--soft);font-size:.8rem;margin-top:24px}}
</style></head><body><div class="wrap">
<h1>Group posts</h1><p class="sub" id="date"></p>
<div class="steps">
<p><b>English:</b> Copy text → Open the Reel → <b>Share</b> → click <b>Group</b> at the bottom (don't type in the first box, don't press "Share now") → pick the group → paste into <b>"Create a public post…"</b> → <b>Post</b>.</p>
<p><b>Other languages:</b> open the group → <b>Create post</b> → <b>Photo/video</b> → pick the file from <b>Downloads → fb-groups</b> → <b>paste</b> → Post.</p>
<p>About a minute each. Every day has its own 3 (the same on every device). Skipped ones come back in the next round.</p></div>
<h2>Today</h2><div id="today"></div>
<details id="ydet"><summary>Missed yesterday? Yesterday's 3</summary><div id="yesterday"></div></details>
<details><summary>All groups, in rotation order</summary><div id="all"></div></details>
<p class="foot">Updated {built}. English Reels refresh from the Facebook page every afternoon.</p>
</div><script>
const D = {blob};
const now = new Date(new Date().toLocaleString("en-US", {{timeZone: "Europe/Oslo"}}));
const ymd = d => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
const dayNo = Math.round((Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) - Date.parse(D.start + "T00:00:00Z")) / 864e5);
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
const N = D.order.length, mod = (a, n) => ((a % n) + n) % n;
function ticks() {{ try {{ return JSON.parse(localStorage.getItem("fbg2") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function tick(k, on) {{ try {{ const t = ticks(); on ? t[k] = 1 : delete t[k]; localStorage.setItem("fbg2", JSON.stringify(t)); }} catch (e) {{}} }}
function slots(day) {{ return [0, 1, 2].map(k => D.groups[D.order[mod(3 * day + k, N)]]); }}
function card(g, i, day, enIdx) {{
  const key = day + "-" + g.name, done = !!ticks()[key];
  let body;
  if (g.code === "en") {{
    const r = D.en.length ? D.en[mod(day * 2 + enIdx, D.en.length)] : null;
    body = r ? `<div class="btns"><a class="btn" href="${{r.url}}" target="_blank" rel="noopener">Open the Reel</a>
      <button class="copy">Copy text</button></div><pre>${{esc(r.text)}}</pre>` : `<p class="none">No English Reel on the page yet.</p>`;
    g._text = r && r.text;
  }} else {{
    const f = D.files[g.code];
    body = f ? `<div class="btns"><span class="file">Upload: <b>${{esc(f.file)}}</b></span><button class="copy">Copy text</button></div><pre>${{esc(f.text)}}</pre>`
             : `<p class="none">No ${{g.lang}} version yet: skip this one.</p>`;
    g._text = f && f.text;
  }}
  const c = document.createElement("div"); c.className = "card" + (done ? " done" : "");
  c.innerHTML = `<div class="top"><div><div class="g">${{esc(g.name)}}</div>
    <div class="meta"><span class="lang">${{g.lang}}</span>${{g.members}} members · ${{esc(g.kind)}}</div></div><div class="num">${{i + 1}}</div></div>` +
    body + `<label><input type="checkbox" ${{done ? "checked" : ""}}> Posted</label>`;
  const b = c.querySelector("button.copy"), text = g._text;
  if (b) b.onclick = () => navigator.clipboard.writeText(text).then(() => {{ b.textContent = "Copied ✓"; setTimeout(() => b.textContent = "Copy text", 1500); }});
  c.querySelector("input").onchange = e => {{ tick(key, e.target.checked); c.classList.toggle("done", e.target.checked); }};
  return c;
}}
function fill(id, day) {{
  const box = document.getElementById(id); let en = 0;
  slots(day).forEach((g, i) => box.appendChild(card(Object.assign({{}}, g), i, day, g.code === "en" ? en++ : 0)));
}}
document.getElementById("date").textContent = now.toLocaleDateString("en-GB", {{weekday: "long", day: "numeric", month: "long"}});
fill("today", dayNo); fill("yesterday", dayNo - 1);
document.getElementById("all").innerHTML = "<table><tr><th>#</th><th>Group</th><th>Language</th></tr>" +
  D.order.map((g, i) => `<tr><td>${{i + 1}}</td><td>${{esc(D.groups[g].name)}}</td><td>${{D.groups[g].lang}}</td></tr>`).join("") + "</table>";
</script></body></html>
"""


def main():
    groups = [{"name": n, "code": l, "lang": LANG[l], "members": m, "kind": k} for n, l, m, k in GROUPS]
    out = page(groups, order(), content())
    if "--push" not in sys.argv:
        p = pathlib.Path(tempfile.gettempdir()) / "groups.html"; p.write_text(out, encoding="utf-8"); print(p); return
    wt = pathlib.Path(tempfile.mkdtemp()) / "gh"
    run = lambda *a, **k: subprocess.run(a, cwd=k.get("cwd", ROOT), check=True, capture_output=True, text=True)
    run("git", "fetch", "-q", "origin", "gh-pages")
    run("git", "worktree", "add", "--detach", str(wt), "origin/gh-pages")
    try:
        f = wt / "groups.html"
        old = f.read_text(encoding="utf-8") if f.exists() else ""
        if re.sub(r"Updated .*? UTC", "", old) == re.sub(r"Updated .*? UTC", "", out):
            print("no change"); return
        f.write_text(out, encoding="utf-8")
        run("git", "add", "groups.html", cwd=wt)
        run("git", "commit", "-m", "Group posts page", cwd=wt)
        run("git", "push", "-q", "origin", "HEAD:gh-pages", cwd=wt)
        print("pushed")
    finally:
        run("git", "worktree", "remove", "--force", str(wt))


if __name__ == "__main__":
    main()
