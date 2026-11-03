#!/usr/bin/env python3
"""The owner's Facebook-groups helper page (owner 2026-10-31: "a file with all content, I just copy-paste"):
groups.html on gh-pages. Meta has no API for posting in groups (removed 2024), so the owner posts by hand.

  · English groups: Open the Reel (on the Page) → Share → Group → paste the text.
  · Other languages: the Page stays English-only (owner 2026-10-31), so their version is a FILE the owner uploads
    into the group (~/Downloads/fb-groups/, listed in data/fb-group-files.json) + the text to paste.

3 + 3 groups a day from 3 Nov 2026 (morning + evening, ~6 h apart; 3 before; owner 2026-11-02), by the calendar (the same on every device), plus yesterday's to
catch up. Not more at once: sharing into many groups in one sitting gets "temporarily blocked from posting in groups".

    python3 tools/fb_groups_page.py           # writes /tmp/groups.html to look at
    python3 tools/fb_groups_page.py --push    # commits groups.html to gh-pages (GitHub: site-latest.yml)

English Reels come from the Facebook Page (only those posted after the app went Live, 30 Oct 2026).
"""
import base64
import hashlib
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

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = "2026-10-30T13:00:00+0000"   # Meta app switched to Live: Reels before this were visible to app roles only
TEMPLATE_VERSION = "2026-11-03a"   # bump when the page layout/script changes, so the next run republishes
START = "2026-11-01"                # day 0 of the rotation
# the owner's groups (2026-10-31); (name, language, members, type). Target 3–5 per language.


def key():
    """The page key (owner 2026-10-31: the group page is private): env GROUPS_KEY (GitHub secret) or
    ~/.config/2min-groups/key. The page and the group list are AES-GCM encrypted with it; the owner's link carries it
    after '#' (never sent to a server)."""
    k = os.environ.get("GROUPS_KEY") or (pathlib.Path.home() / ".config/2min-groups/key").read_text().strip()
    return base64.urlsafe_b64decode(k + "=" * (-len(k) % 4))


def seal(text):
    nonce = os.urandom(12)
    return base64.b64encode(nonce + AESGCM(key()).encrypt(nonce, text.encode("utf-8"), None)).decode()


def unseal(blob):
    raw = base64.b64decode(blob)
    return AESGCM(key()).decrypt(raw[:12], raw[12:], None).decode("utf-8")


# the owner's groups (final list 31 Oct 2026, joined as the Page), encrypted in data/fb-groups.enc (the repo is public):
# name, lang, members, kind, url (→ "Open the group"). Read/change: --show-groups > x.json · edit · --set-groups x.json
_G = json.loads(unseal((ROOT / "data" / "fb-groups.enc").read_text()))
# to drop a group later: set "dropped": "<date>: why" in its entry (--show-groups/--set-groups) instead of deleting it —
# deleting shifts every later day's groups and breaks the owner's ticks
GROUPS = [(x["name"], x["lang"], x["members"], x["kind"]) for x in _G]
DROPPED = {x["name"] for x in _G if x.get("dropped")}
URLS = {x["name"]: x.get("url", "") for x in _G}
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
    tail = [CLOSE[lang], "▶️ Full lessons: 2 Minute Arabic on YouTube" if lang == "en" else "▶️ YouTube: 2 Minute Arabic"]   # name only, no URL (group rules)
    if lang == "en":   # a shared Reel already shows its own caption (owner 2026-11-03): only the hook + who we are
        hook = re.sub(r"^Day \d+ of 30 — ", "", keep[0].splitlines()[0]) if keep else ""
        return "\n\n".join([hook[:1].upper() + hook[1:]] + tail)
    return "\n\n".join(keep + tail)


def content():
    # oldest first: round r of the rotation shares English Reel r with every English group (owner 2026-11-01: "the previous
    # one hasn't gone to all groups") — one Reel goes round all groups, then the next
    en = [v for v in sorted(reels(), key=lambda v: v["created_time"]) if is_english(v["description"])]
    files = json.loads((ROOT / "data" / "fb-group-files.json").read_text(encoding="utf-8"))
    return {
        "en": [{"url": "https://www.facebook.com" + v["permalink_url"], "title": v["description"].splitlines()[0][:90],
                "text": paste_text(v["description"], "en")} for v in en],
        "files": {l: {"file": f["file"], "title": f["video"], "text": paste_text(f["caption"], l)} for l, f in files.items()},
    }


def page(groups, rotation, data):
    plain = json.dumps({"groups": groups, "order": rotation, "start": START, **data}, ensure_ascii=False)
    blob = seal(plain)
    fp = hashlib.sha256((plain + TEMPLATE_VERSION).encode()).hexdigest()[:16]   # content fingerprint: the ciphertext changes every run
    built = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Group posts</title><link rel="icon" href="favicon.png">
<style>
:root{{--bg:#fbf6ee;--card:#fff;--ink:#2a2420;--soft:#6f6258;--teal:#1f6f6b;--terra:#c8643b;--line:#eadfce}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1a17;--card:#27231f;--ink:#f3ece3;--soft:#b9ab9c;--line:#3a332c;--teal:#5fb3ad;--terra:#e08a63}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:640px;margin:0 auto;padding:20px 16px 48px}}
h1{{font-size:1.5rem;margin:0 0 4px}} h3{{font-size:1rem;margin:14px 0 8px;color:var(--soft)}} h2{{font-size:1.1rem;margin:26px 0 10px}} .sub{{color:var(--soft);margin:0 0 18px}}
.steps{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:18px;color:var(--soft);font-size:.95rem}}
.steps b{{color:var(--ink)}} .steps p{{margin:4px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:10px}}a.g{{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line)}}a.g:hover{{color:var(--teal)}}button.name{{background:var(--bg);color:var(--ink);border:1px solid var(--line);padding:4px 10px;font-size:.85rem}}.btns{{margin:8px 0 8px}}label{{margin-top:6px}}
.card{{background:color-mix(in srgb,var(--terra) 14%,var(--card));border-color:color-mix(in srgb,var(--terra) 45%,var(--line))}}@media (prefers-color-scheme:dark){{.card{{background:#4a3a2b;border-color:#7a5a3c}}.card .box pre{{background:#1f1b18}}}}.card.done{{opacity:.55;background:#d6d6d6}}@media (prefers-color-scheme:dark){{.card.done{{background:#3a3a3a}}}}
.top{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.top .right{{margin-left:auto;display:flex;gap:8px;align-items:center;white-space:nowrap}}.top .meta{{display:flex;gap:6px;align-items:center}}.top .lang{{margin:0}}.tick{{margin:0;display:flex;gap:6px;align-items:center;font-weight:600}}.card.done pre,.card.done button.copy,.card.done .btns{{display:none}}.card.done{{padding-bottom:8px;padding-top:8px;border-color:transparent}}.btns{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.btns .meta{{margin-left:auto;display:flex;gap:6px;align-items:center}}.box{{position:relative}}.box pre{{padding-right:120px}}.box button.copy{{position:absolute;top:8px;right:8px;padding:8px 12px}}.head{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}.tips{{margin-left:auto;display:flex;gap:6px}}button.tip{{position:relative;background:var(--card);color:var(--soft);border:1px solid var(--line);font-size:.8rem;padding:4px 10px}}.tip .pop{{display:none;position:absolute;right:0;top:110%;width:min(320px,85vw);background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:12px;font-weight:400;font-size:.9rem;text-align:left;box-shadow:0 6px 24px rgba(0,0,0,.25);z-index:5}}.tip:hover .pop,.tip:focus .pop,.tip:focus-within .pop{{display:block}}
.num{{background:var(--terra);color:#fff;border-radius:50%;width:30px;height:30px;display:grid;place-items:center;font-weight:700;flex:none}}
.g{{font-weight:700;font-size:1.08rem}} .meta{{color:var(--soft);font-size:.88rem}}
.lang.en{{background:#d93025!important}}.lang{{display:inline-block;background:var(--teal);color:#fff;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:600;margin-right:6px}}
.btns{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px;align-items:center}}
a.btn,button{{font:inherit;font-weight:600;border-radius:10px;padding:10px 14px;border:0;cursor:pointer;text-decoration:none}}
a.btn{{background:var(--teal);color:#fff}} a.btn.grp{{background:#3b5998}} button.copy{{background:var(--terra);color:#fff}}
.file{{background:var(--bg);border:1px dashed var(--teal);border-radius:10px;padding:8px 12px;font-size:.93rem}}
.file b{{font-family:ui-monospace,monospace}}
pre{{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px;margin:0;font:inherit;font-size:.93rem;max-height:4.6em;line-height:1.45;overflow:auto}}
label{{display:flex;gap:8px;align-items:center;margin-top:10px;font-weight:600}} input{{width:20px;height:20px}}
.none{{color:var(--soft);font-style:italic}}
details{{margin-top:26px}} summary{{cursor:pointer;font-weight:700}}
table{{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:10px}} td,th{{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left;vertical-align:top}}
.foot{{color:var(--soft);font-size:.8rem;margin-top:24px}}
</style></head><body><div class="wrap">
<div id="locked" hidden><h1>Private page</h1><p class="sub">This page is private.</p></div>
<div id="app" hidden><div class="head"><h1>Group posts</h1><span class="tips">
<button class="tip" type="button">English ?<span class="pop"><b>English:</b> Copy text → Open the Reel → <b>Share</b> → click <b>Group</b> at the bottom (don't type in the first box, don't press "Share now") → pick the group → paste into <b>"Create a public post…"</b> → <b>Post</b>.</span></button>
<button class="tip" type="button">Other ?<span class="pop"><b>Other languages:</b> open the group → <b>Create post</b> → <b>Photo/video</b> → pick the file from <b>Downloads → fb-groups</b> → <b>paste</b> → Post.<br><br>Every day: a morning 3 and an evening 3, about 6 hours apart (the same on every device). Skipped ones come back in the next round.</span></button>
</span></div><p class="sub" id="date"></p>
<h2>Today</h2><div id="today"></div>
<details id="ydet"><summary>Missed yesterday? Yesterday's groups</summary><div id="yesterday"></div></details>
<details><summary>All groups, in rotation order</summary><div id="all"></div></details>
</div><p class="foot" id="foot" data-built="{built}" data-fp="{fp}"></p>
</div><script>
const SEALED = "{blob}";
(async () => {{
  let D;
  try {{
    let k = location.hash.startsWith("#k=") ? location.hash.slice(3) : null;
    try {{ k = k || localStorage.getItem("gk"); }} catch (e) {{}}
    const b = s => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4)), c => c.charCodeAt(0));
    const raw = b(SEALED), ck = await crypto.subtle.importKey("raw", b(k), "AES-GCM", false, ["decrypt"]);
    D = JSON.parse(new TextDecoder().decode(await crypto.subtle.decrypt({{name: "AES-GCM", iv: raw.slice(0, 12)}}, ck, raw.slice(12))));
    try {{ localStorage.setItem("gk", k); }} catch (e) {{}}
    if (location.hash) history.replaceState(null, "", location.pathname);
  }} catch (e) {{ document.getElementById("locked").hidden = false; return; }}
  document.getElementById("app").hidden = false;
  main(D);
}})();
function main(D) {{
const now = new Date(new Date().toLocaleString("en-US", {{timeZone: "Europe/Oslo"}}));
const ymd = d => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
const dayNo = Math.round((Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) - Date.parse(D.start + "T00:00:00Z")) / 864e5);
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
const N = D.order.length, mod = (a, n) => ((a % n) + n) % n;
function ticks() {{ try {{ return JSON.parse(localStorage.getItem("fbg2") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function tick(k, on) {{ try {{ const t = ticks(); on ? t[k] = Date.now() : delete t[k]; localStorage.setItem("fbg2", JSON.stringify(t)); }} catch (e) {{}} }}
// the evening 3 open 6 h after the LAST of the morning 3 was ticked (owner 2026-11-02)
const GAP = 6 * 3600e3;
function eveningOpensAt(day) {{
  const t = ticks(), times = slots(day).slice(0, 3).map(g => t[day + "-" + g.name]);
  if (slots(day).slice(0, 3).some((g, k) => !times[k] && !g.dropped)) return null;                                   // morning not finished yet
  return Math.max(0, ...times.filter(Boolean).map(x => x === 1 ? 0 : x)) + GAP;               // 1 = ticked before this rule: open now
}}
// 3 a day until 2 Nov, 5 a day from 3 Nov (owner 2026-11-02) — the rotation continues where it was
const per = day => day < 1 ? 3 : 6;   // 3 + 3: a morning and an evening session ~6 h apart (owner 2026-11-02)
const first = day => day < 1 ? 3 * day : 3 + 6 * (day - 1);
function slots(day) {{ return Array.from({{length: per(day)}}, (_, k) => D.groups[D.order[mod(first(day) + k, N)]]); }}
// a dropped group (no posting allowed) counts as done, so its session can still finish and it shows as a slim note
const isDone = (t, day, g) => g.dropped || !!t[day + "-" + g.name];
function card(g, i, day, enIdx) {{
  const key = day + "-" + g.name, done = !!ticks()[key];
  let body;
  if (g.code === "en") {{
    // the round this card belongs to (round 0 = 31 Oct–7 Nov, the first one the owner posted): the same Reel for all
    const round = Math.floor((first(day) + i + 3) / N);
    const r = D.en.length ? D.en[Math.min(Math.max(round, 0), D.en.length - 1)] : null;
    body = r ? `<div class="btns"><a class="btn" href="${{r.url}}" target="_blank" rel="noopener">Open the Reel</a>
</div><pre>${{esc(r.text)}}</pre><button class="copy">Copy text</button>` : `<p class="none">No English Reel on the page yet.</p>`;
    g._text = r && r.text;
  }} else {{
    const f = D.files[g.code];
    body = f ? `<div class="btns"><span class="file">Upload: <b>${{esc(f.file)}}</b></span></div><pre>${{esc(f.text)}}</pre><button class="copy">Copy text</button>`
             : `<p class="none">No ${{g.lang}} version yet: skip this one.</p>`;
    g._text = f && f.text;
  }}
  const c = document.createElement("div"); c.className = "card" + (done ? " done" : "");
  c.innerHTML = `<div class="top"><button class="name">Copy name</button>
    ${{g.url ? `<a class="g" href="${{g.url}}" target="_blank" rel="noopener">${{esc(g.name)}}</a>` : `<span class="g">${{esc(g.name)}}</span>`}}
    <span class="right"><label class="tick"><input type="checkbox" ${{done ? "checked" : ""}}> Posted</label><span class="num">${{i + 1}}</span></span></div>` +
    body.replace('<div class="btns">', `<div class="btns">`).replace("</div><pre>", `<span class="meta">${{g.members}} members <span class="lang${{g.code === "en" ? " en" : ""}}">${{g.lang}}</span></span></div><div class="box"><pre>`).replace('<button class="copy">Copy text</button>', '<button class="copy">Copy text</button></div>');
  const b = c.querySelector("button.copy"), text = g._text;
  c.querySelector("button.name").onclick = e => navigator.clipboard.writeText(g.name.replace(/ \\(.*\\)$/, "")).then(() => {{ e.target.textContent = "Copied ✓"; setTimeout(() => e.target.textContent = "Copy name", 1500); }});
  if (b) b.onclick = () => navigator.clipboard.writeText(text).then(() => {{ b.textContent = "Copied ✓"; setTimeout(() => b.textContent = "Copy text", 1500); }});
  c.querySelector("input").onchange = e => {{ tick(key, e.target.checked); c.classList.toggle("done", e.target.checked); if (i < 3) render(); }};
  return c;
}}
const span2 = ms => {{ const m = Math.max(1, Math.round(ms / 60000)), h = Math.floor(m / 60); return h ? `${{h}} h ${{m % 60}} min` : `${{m}} min`; }};
function fill(id, day, lockEvening) {{
  const box = document.getElementById(id); box.innerHTML = ""; let en = 0;
  const opens = eveningOpensAt(day), t = ticks();
  slots(day).forEach((g, i) => {{
    if (per(day) > 3 && i % 3 === 0) box.insertAdjacentHTML("beforeend", `<h3>${{i ? "Evening" : "Morning"}}</h3>`);
    const isEn = g.code === "en", idx = isEn ? en++ : 0;
    if (g.dropped) {{ box.insertAdjacentHTML("beforeend", `<div class="card done"><span class="g">${{esc(g.name)}}</span> <span class="meta">— skipped: no posting allowed</span></div>`); return; }}
    if (lockEvening && i >= 3 && !t[day + "-" + g.name] && (opens === null || Date.now() < opens)) {{
      if (!box.querySelector(".locked")) box.insertAdjacentHTML("beforeend", `<div class="card locked"><p class="none">${{opens === null
        ? "Opens 6 hours after you tick the 3rd morning group."
        : `Opens in ${{span2(opens - Date.now())}} (at ${{new Date(opens).toLocaleTimeString("en-GB", {{hour: "2-digit", minute: "2-digit"}})}}) — 6 hours after your morning posts.`}}</p></div>`);
      return;
    }}
    box.appendChild(card(Object.assign({{}}, g), i, day, idx));
  }});
}}
function render() {{ fill("today", dayNo, true); }}
// footer: last update + countdown to the next one (site-latest.yml runs hourly at :25, 05–20 UTC)
const UPD = Array.from({{length: 16}}, (_, k) => 5 + k).map(h => h);  // checks at :05 (laptop) and :25 (GitHub)
function footer() {{
  const f = document.getElementById("foot"), built = new Date(f.dataset.built), t = new Date();
  let next = null;
  for (let d = 0; d < 2 && !next; d++) for (const h of UPD) {{
    const c = new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() + d, h, 25));
    if (c > t) {{ next = c; break; }}
  }}
  const span = ms => {{ const m = Math.round(Math.abs(ms) / 60000), h = Math.floor(m / 60);
    return h ? `${{h}} h ${{m % 60}} min` : `${{m}} min`; }};
  const at = d => d.toLocaleString("en-GB", {{timeZone: "Europe/Oslo", weekday: "short", hour: "2-digit", minute: "2-digit"}});
  f.textContent = `Content last changed ${{span(t - built)}} ago (${{at(built)}}) · checked every hour, next check in about ${{span(next - t)}}`;
}}
footer(); setInterval(footer, 60000);
document.getElementById("date").textContent = now.toLocaleDateString("en-GB", {{weekday: "long", day: "numeric", month: "long"}});
render(); setInterval(() => {{ if (document.querySelector(".card.locked")) render(); }}, 60000); fill("yesterday", dayNo - 1, false);
document.getElementById("all").innerHTML = "<table><tr><th>#</th><th>Group</th><th>Language</th></tr>" +
  D.order.map((g, i) => `<tr><td>${{i + 1}}</td><td>${{esc(D.groups[g].name)}}</td><td>${{D.groups[g].lang}}</td></tr>`).join("") + "</table>";
}}
</script></body></html>
"""


def main():
    if "--show-groups" in sys.argv:
        print(json.dumps(_G, ensure_ascii=False, indent=1)); return
    if "--set-groups" in sys.argv:
        src = pathlib.Path(sys.argv[sys.argv.index("--set-groups") + 1])
        (ROOT / "data" / "fb-groups.enc").write_text(seal(json.dumps(json.loads(src.read_text(encoding="utf-8")), ensure_ascii=False)) + "\n")
        print("data/fb-groups.enc updated"); return
    groups = [{"name": n, "code": l, "lang": LANG[l], "members": m, "kind": k, "url": URLS.get(n, ""), "dropped": n in DROPPED} for n, l, m, k in GROUPS]
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
        if re.search(r'data-fp="([^"]*)"', old) and re.search(r'data-fp="([^"]*)"', old).group(1) == re.search(r'data-fp="([^"]*)"', out).group(1):
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
