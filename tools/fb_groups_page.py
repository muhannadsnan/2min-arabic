#!/usr/bin/env python3
"""The owner's Facebook-groups helper page (owner 2026-10-31: "a file with all content, I just copy-paste"):
groups.html on gh-pages — the next 3 groups in the rotation (any day: owner 2026-10-31, "sometimes I have time at
the weekend, sometimes not"), each with the newest page Reel in that
group's language, an "Open the Reel" button and the text to paste with a Copy button. Meta has no API for posting
in groups (removed 2024), so the owner shares by hand: Reel → Share → Group → paste. 3 a day, not 15 at once:
sharing to many groups in one sitting gets "temporarily blocked from posting in groups".

    python3 tools/fb_groups_page.py           # writes /tmp/groups.html to look at
    python3 tools/fb_groups_page.py --push    # commits groups.html to gh-pages (GitHub: site-latest.yml)

Reels come from the Facebook Page (only those posted after the app went Live, 30 Oct 2026 — older ones were never
shown to anyone). What's done is remembered in the browser (the "Posted" ticks): the page shows the 3 groups posted
to longest ago, and stops at 3 a day.
"""
import datetime
import html
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
# owner's 15 groups (2026-10-31), in the order they're used; (name, language, members, type)
GROUPS = [
    ("Learn Arabic in English", "en", "561K", "busy"),
    ("Arabic Language Learners", "en", "236K", "busy"),
    ("Let's Learn Arabic", "en", "152K", "busy"),
    ("Learn Spoken Arabic", "en", "72K", "busy"),
    ("Learning simple arabic for beginners", "en", "42K", "busy"),
    ("Learn Arabic Language - MSA Arabic - Egyptian Arabic - Gulf Arabic", "en", "30K", "medium"),
    ("Arabic Learning in English and Urdu", "ur", "340K", "quiet, admin approval — Urdu/English/Arabic only"),
    ("Arabic English Lessons", "hi", "38K", "busy"),
    ("Belajar Bahasa Arab", "id", "221K", "medium"),
    ("Belajar Bahasa Arab (the one with the اللغة العربية logo)", "id", "109K", "medium"),
    ("Komunitas belajar bahasa arab", "id", "52K", "busy"),
    ("BELAJAR BAHASA ARAB (PEMULA)", "id", "12K", "quiet"),
    ("Arapça Dersi", "tr", "139K", "quiet"),
    ("Arapça Öğrenmek İsteyenler", "tr", "11K", "quiet"),
    ("Arapça Ders Öğren İrap Tahlil Cümle", "tr", "37K", "busy"),
]
# rotation order: every 3 in a row are different languages where possible (index into GROUPS)
ORDER = [0, 6, 8, 1, 7, 12, 2, 9, 13, 3, 10, 14, 4, 11, 5]
LANG = {"en": "English", "ur": "Urdu", "hi": "Hindi", "id": "Indonesian", "tr": "Turkish", "ms": "Malay"}
CLOSE = {
    "en": "I'm a native Syrian Arabic speaker and post a 2-minute lesson every day. Questions welcome 🙂",
    "ur": "میں شام (سیریا) سے ہوں اور روز 2 منٹ کا عربی سبق بناتا ہوں۔ کوئی سوال ہو تو ضرور پوچھیں 🙂",
    "hi": "Main Syria se hoon aur roz 2 minute ka Arabic lesson banata hoon. Koi sawal ho to zaroor poochhein 🙂",
    "id": "Saya penutur asli bahasa Arab dari Suriah dan membuat pelajaran 2 menit setiap hari. Silakan bertanya 🙂",
    "ms": "Saya penutur asli bahasa Arab dari Syria dan membuat pelajaran 2 minit setiap hari. Silakan bertanya 🙂",
    "tr": "Suriyeliyim, ana dilim Arapça. Her gün 2 dakikalık bir ders paylaşıyorum. Sorularınızı bekliyorum 🙂",
}


def creds():
    if os.environ.get("FB_PAGE_TOKEN"):
        return os.environ["FB_PAGE_TOKEN"]
    return json.loads((pathlib.Path.home() / ".config/2min-facebook/page.json").read_text())["page_token"]


def reels():
    q = urllib.parse.urlencode({"fields": "id,created_time,description,permalink_url", "limit": 40, "access_token": creds()})
    with urllib.request.urlopen(f"https://graph.facebook.com/v21.0/me/video_reels?{q}", timeout=60) as r:
        data = json.load(r)["data"]
    return [v for v in data if v["created_time"] > LIVE and v.get("description")]


def language(caption):
    first = caption.strip().splitlines()[0]
    if re.search(r"[ऀ-ॿ]", first): return "hi"
    if re.search(r"[ٹڈڑںےہھ]", first): return "ur"
    if "Arapça" in first: return "tr"
    if re.search(r"\b(tiada|minit)\b", first): return "ms"
    if re.search(r"bahasa Arab", first, re.I): return "id"
    return "en"


def paste_text(caption, lang):
    """The lesson part of the caption + a friendly line; drops hashtags, other-language lines and 'link in bio'."""
    keep = [p for p in caption.strip().split("\n\n")
            if not re.search(r"#|🌍|link|bio|लिंक|لنک|profil|YouTube", p, re.I)]
    return "\n\n".join(keep + [CLOSE[lang]])


def plan():
    by_lang = {}
    for v in sorted(reels(), key=lambda v: v["created_time"], reverse=True):
        by_lang.setdefault(language(v["description"]), []).append(v)
    items, used = [], {}
    for g in ORDER:   # groups of one language get that language's Reels newest first, so they don't all share one
        name, lang, members, kind = GROUPS[g]
        mine = by_lang.get(lang, []); n = used.get(lang, 0); used[lang] = n + 1
        item = {"id": g, "group": name, "lang": LANG[lang], "members": members, "kind": kind}
        if mine:
            v = mine[n % len(mine)]
            item.update(url="https://www.facebook.com" + v["permalink_url"], title=v["description"].splitlines()[0][:90],
                        text=paste_text(v["description"], lang))
        items.append(item)
    return items


def page(items):
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    built = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %H:%M UTC")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Group posts</title><link rel="icon" href="favicon.png">
<style>
:root{{--bg:#fbf6ee;--card:#fff;--ink:#2a2420;--soft:#6f6258;--teal:#1f6f6b;--terra:#c8643b;--line:#eadfce;--ok:#2e7d4f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1a17;--card:#27231f;--ink:#f3ece3;--soft:#b9ab9c;--line:#3a332c;--teal:#5fb3ad;--terra:#e08a63}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:640px;margin:0 auto;padding:20px 16px 48px}}
h1{{font-size:1.5rem;margin:0 0 4px}} .sub{{color:var(--soft);margin:0 0 18px}}
.steps{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:18px;color:var(--soft);font-size:.95rem}}
.steps b{{color:var(--ink)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}}
.card.done{{opacity:.55}}
.top{{display:flex;gap:10px;align-items:flex-start;justify-content:space-between}}
.num{{background:var(--terra);color:#fff;border-radius:50%;width:30px;height:30px;display:grid;place-items:center;font-weight:700;flex:none}}
.g{{font-weight:700;font-size:1.08rem}} .meta{{color:var(--soft);font-size:.88rem}}
.lang{{display:inline-block;background:var(--teal);color:#fff;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:600;margin-right:6px}}
.btns{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px}}
a.btn,button{{font:inherit;font-weight:600;border-radius:10px;padding:10px 14px;border:0;cursor:pointer;text-decoration:none}}
a.btn{{background:var(--teal);color:#fff}} button.copy{{background:var(--terra);color:#fff}}
pre{{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px;margin:0;font:inherit;font-size:.93rem;max-height:220px;overflow:auto}}
label{{display:flex;gap:8px;align-items:center;margin-top:10px;font-weight:600}} input{{width:20px;height:20px}}
.none{{color:var(--soft);font-style:italic}}
details{{margin-top:26px}} summary{{cursor:pointer;font-weight:700}}
table{{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:10px}} td,th{{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left;vertical-align:top}}
.foot{{color:var(--soft);font-size:.8rem;margin-top:24px}}
</style></head><body><div class="wrap">
<h1>Group posts</h1><p class="sub" id="date"></p>
<div class="steps"><b>For each:</b> Open the Reel → <b>Share</b> → <b>Group</b> → search the group name → <b>paste</b> the text → Post → tick <b>Posted</b>. About a minute each. Up to 3 a day, any day.</div>
<div id="today"></div>
<details><summary>All 15 groups (last posted)</summary><div id="all"></div></details>
<p class="foot">Updated {built} from the Facebook page. Reels refresh every afternoon. Your ticks are remembered on this device.</p>
</div><script>
const ITEMS = {data};
const now = new Date(new Date().toLocaleString("en-US", {{timeZone: "Europe/Oslo"}}));
const today = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
function load() {{ try {{ return JSON.parse(localStorage.getItem("fbgroups") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function save(v) {{ try {{ localStorage.setItem("fbgroups", JSON.stringify(v)); }} catch (e) {{}} }}
let last = load();   // group id -> date posted
document.getElementById("date").textContent = now.toLocaleDateString("en-GB", {{weekday: "long", day: "numeric", month: "long"}});
function render() {{
  const box = document.getElementById("today"); box.innerHTML = "";
  const doneToday = ITEMS.filter(it => last[it.id] === today);
  // longest ago first (never = first), rotation order breaks ties
  const queue = ITEMS.map((it, i) => [last[it.id] || "", i, it]).sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] - b[1]).map(x => x[2]);
  const show = doneToday.concat(queue.filter(it => last[it.id] !== today).slice(0, Math.max(0, 3 - doneToday.length)));
  if (doneToday.length >= 3) box.insertAdjacentHTML("beforeend", '<div class="card"><p class="none">Done for today ✓ Three a day keeps Facebook happy. Next 3 whenever you have time, from tomorrow.</p></div>');
  show.forEach((it, i) => {{
    const done = last[it.id] === today;
    const c = document.createElement("div"); c.className = "card" + (done ? " done" : "");
    c.innerHTML = `<div class="top"><div><div class="g">${{esc(it.group)}}</div>
      <div class="meta"><span class="lang">${{it.lang}}</span>${{it.members}} members · ${{esc(it.kind)}}</div></div><div class="num">${{i + 1}}</div></div>` +
      (it.url ? `<div class="btns"><a class="btn" href="${{it.url}}" target="_blank" rel="noopener">Open the Reel</a>
        <button class="copy">Copy text</button></div><pre>${{esc(it.text)}}</pre>`
              : `<p class="none">No ${{it.lang}} Reel on the page yet: tick it to skip for now.</p>`) +
      `<label><input type="checkbox" ${{done ? "checked" : ""}}> Posted</label>`;
    const b = c.querySelector("button.copy");
    if (b) b.onclick = () => navigator.clipboard.writeText(it.text).then(() => {{ b.textContent = "Copied ✓"; setTimeout(() => b.textContent = "Copy text", 1500); }});
    c.querySelector("input").onchange = e => {{ if (e.target.checked) last[it.id] = today; else delete last[it.id]; save(last); render(); }};
    box.appendChild(c);
  }});
  document.getElementById("all").innerHTML = "<table><tr><th>Group</th><th>Language</th><th>Last posted</th></tr>" +
    ITEMS.map(it => `<tr><td>${{esc(it.group)}}</td><td>${{it.lang}}</td><td>${{last[it.id] || "—"}}</td></tr>`).join("") + "</table>";
}}
render();
</script></body></html>
"""


def main():
    out = page(plan())
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
