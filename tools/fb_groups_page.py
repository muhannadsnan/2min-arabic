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
TEMPLATE_VERSION = "2026-11-08e"   # bump when the page layout/script changes, so the next run republishes
START = "2026-11-01"                # day 0 of the rotation
# 2026-11-09 (owner 2026-11-08: "more groups so the circle gets bigger" — admins approve slowly, a post every 4 days was
# too often): 23 → 47 groups, still 6 a day ≈ 8 days a round. Days before EPOCH keep the old rotation of the first
# OLD_N groups (ticks + history stay right); from EPOCH a new rotation of all groups, and each old group continues
# with the video after the one its last old turn showed (new groups start at the first video).
EPOCH, OLD_N = "2026-11-09", 23
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
START_IDX = {x["name"]: x["start"] for x in _G if x.get("start")}
SHARE = {x["name"] for x in _G if x.get("share")}
TODO = {x["name"]: x["todo"] for x in _G if x.get("todo")}   # an open question for the owner (shown on the to-do card)   # new group already posted to by hand before its first turn
LANG = {"en": "English", "ur": "Urdu", "hi": "Hindi", "id": "Indonesian", "tr": "Turkish", "ms": "Malay"}
CLOSE = {
    "en": "I'm a native Syrian Arabic speaker and post a 2-minute lesson every day. Questions welcome 🙂",
    "ur": "میں شام (سیریا) سے ہوں اور روز 2 منٹ کا عربی سبق بناتا ہوں۔ کوئی سوال ہو تو ضرور پوچھیں 🙂",
    "hi": "Main Syria se hoon aur roz 2 minute ka Arabic lesson banata hoon. Koi sawal ho to zaroor poochhein 🙂",
    "id": "Saya penutur asli bahasa Arab dari Suriah dan membuat pelajaran 2 menit setiap hari. Silakan bertanya 🙂",
    "ms": "Saya penutur asli bahasa Arab dari Syria dan membuat pelajaran 2 minit setiap hari. Silakan bertanya 🙂",
    "tr": "Suriyeliyim, ana dilim Arapça. Her gün 2 dakikalık bir ders paylaşıyorum. Sorularınızı bekliyorum 🙂",
}


def order(groups=None):
    """Rotation: each language's groups spread evenly over the round (English has 10 of 23), so a day rarely gets
    the same language twice."""
    by = {}
    for i, g in enumerate(GROUPS if groups is None else groups):
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


# share-mode groups (owner 2026-11-08): a language group that blocks video uploads but lets members SHARE → it gets the
# English Reel, with the paste text in its own language (who we are + the YouTube subtitles in that language)
SUBS = {"id": "▶️ YouTube: 2 Minute Arabic (ada subtitle bahasa Indonesia)", "ms": "▶️ YouTube: 2 Minute Arabic (ada sari kata Bahasa Melayu)",
        "tr": "▶️ YouTube: 2 Minute Arabic (Türkçe altyazılı)", "ur": "▶️ YouTube: 2 Minute Arabic (اردو سب ٹائٹلز کے ساتھ)",
        "hi": "▶️ YouTube: 2 Minute Arabic (Hindi subtitles ke saath)"}


def share_text(caption, lang):
    hook = paste_text(caption, "en").split("\n\n")[0]
    return "\n\n".join([hook, CLOSE[lang], SUBS[lang]])


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
                "text": paste_text(v["description"], "en"),
                "local": {l: share_text(v["description"], l) for l in SUBS}} for v in en],
        # one video per round per language, like the English Reels (owner 2026-11-07: a group got Day 12 again while its last
        # Day 12 post was still pending) — data/fb-group-files.json: {lang: [round 0, round 1, …]}, the last one repeats
        "files": {l: [{"file": f["file"], "title": f["video"], "text": paste_text(f["caption"], l)} for f in fs] for l, fs in files.items()},
        # the YouTube Post that goes with each carousel (tools/yt_post.py; owner 2026-11-04) — shown on its day
        "yt": json.loads((ROOT / "data" / "yt-posts.json").read_text(encoding="utf-8")) if (ROOT / "data" / "yt-posts.json").exists() else [],
    }


def page(groups, rotation, data):
    plain = json.dumps({"groups": groups, "order": rotation, "order_old": order(GROUPS[:OLD_N]), "start": START,
                        "epoch": EPOCH, **data}, ensure_ascii=False)
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
/* one colour per language (owner 2026-11-07) */.vt{{display:block;max-width:15em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:default}}.lang{{min-width:7.4em;text-align:center;box-sizing:border-box}}.lang.en{{background:#d93025!important}}.lang.id{{background:#1f7a4d!important}}.lang.tr{{background:#c2620a!important}}.lang.hi{{background:#7b3fc4!important}}.lang.ur{{background:#0b7285!important}}.lang.ms{{background:#c2255c!important}}.lang{{display:inline-block;background:var(--teal);color:#fff;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:600;margin-right:6px}}
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
button.pend{{background:var(--bg);color:var(--soft);border:1px solid var(--line);padding:4px 10px;font-size:.8rem}}.card.done button.pend.on{{color:var(--terra);border-color:var(--terra)}}.note{{margin:8px 0 0;color:var(--terra);font-size:.88rem;font-weight:600}}.card.done .note{{display:none}}
</style></head><body><div class="wrap">
<div id="locked" hidden><h1>Private page</h1><p class="sub">This page is private.</p></div>
<div id="app" hidden><div class="head"><h1>Group posts</h1><span class="tips">
<button class="tip" type="button">English ?<span class="pop"><b>English:</b> Copy text → Open the Reel → <b>Share</b> → click <b>Group</b> at the bottom (don't type in the first box, don't press "Share now") → pick the group → paste into <b>"Create a public post…"</b> → <b>Post</b>.</span></button>
<button class="tip" type="button">Other ?<span class="pop"><b>Other languages:</b> open the group → <b>Create post</b> → <b>Photo/video</b> → pick the file from <b>Downloads → fb-groups</b> → <b>paste</b> → Post.<br><br><b>"You have a pending post"</b> in a group (the admins haven't approved the last one yet)? Don't post again: tap <b>Still pending</b>. The group is skipped today, gets the video it missed next round, and its card reminds you to check first.<br><br>Every day: a morning 3 and an evening 3, about 6 hours apart (the same on every device). Skipped ones come back in the next round.</span></button>
</span></div><p class="sub" id="date"></p>
<div id="todo"></div><h2>Today</h2><div id="today"></div>
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
const N = D.order.length, NO = D.order_old.length, mod = (a, n) => ((a % n) + n) % n;
const E = Math.round((Date.parse(D.epoch + "T00:00:00Z") - Date.parse(D.start + "T00:00:00Z")) / 864e5);   // first day of the big rotation
function ticks() {{ try {{ return JSON.parse(localStorage.getItem("fbg2") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function tick(k, on) {{ try {{ const t = ticks(); on ? t[k] = Date.now() : delete t[k]; localStorage.setItem("fbg2", JSON.stringify(t)); }} catch (e) {{}} }}
// groups whose last post still waits for admin approval (owner 2026-11-06): {{name: {{day, date, n}}}} — n = rounds in a row
function pends() {{ try {{ return JSON.parse(localStorage.getItem("fbgp") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function setPend(name, v) {{ try {{ const p = pends(); v ? p[name] = v : delete p[name]; localStorage.setItem("fbgp", JSON.stringify(p)); }} catch (e) {{}} }}
// which video each group got (owner 2026-11-07: "that group has not got the x03"): {{"day-name": video index}}. A group
// skipped as pending gets the video it missed next time and never jumps one; on-time groups follow the round.
function sentLog() {{ try {{ return JSON.parse(localStorage.getItem("fbgs") || "{{}}"); }} catch (e) {{ return {{}}; }} }}
function logSent(k, idx) {{ try {{ const s = sentLog(); idx === null ? delete s[k] : s[k] = idx; localStorage.setItem("fbgs", JSON.stringify(s)); }} catch (e) {{}} }}
const oldRound = (day, k) => Math.max(Math.floor((first(day) + k + 3) / NO), 0);
let BASE = null;   // the video each old group gets at its first turn in the big rotation = the one after its last old turn
function base(name) {{
  if (!BASE) {{ BASE = {{}}; D.order_old.forEach(gi => {{ const nm = D.groups[gi].name;
    for (let d = E - 1; d > E - 40; d--) {{ const k = slots(d).findIndex(x => x.name === nm); if (k >= 0) {{ BASE[nm] = oldRound(d, k) + 1; break; }} }} }}); }}
  return BASE[name] || (D.groups.find(g => g.name === name) || {{}}).start || 0;   // new groups: the first video, or "start" if posted early by hand
}}
const roundOf = (day, k) => day < E ? oldRound(day, k) : base(slots(day)[k].name) + Math.floor((6 * (day - E) + k) / N);
function videoIdx(g, day, i, n) {{
  const round = roundOf(day, i), s = sentLog(), mine = Object.keys(s).filter(k => k.endsWith("-" + g.name)).map(k => s[k]);
  let idx = round;
  if (mine.length) idx = Math.min(Math.max(...mine) + 1, round);
  else {{ const pr = pends()[g.name];                                   // skipped before this log existed: the round it missed
    if (pr && pr.day < day) {{ const k = slots(pr.day).findIndex(x => x.name === g.name); if (k >= 0) idx = roundOf(pr.day, k); }} }}
  return Math.max(0, Math.min(idx, n - 1));
}}
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
function slots(day) {{ return Array.from({{length: per(day)}}, (_, k) => day < E ? D.groups[D.order_old[mod(first(day) + k, NO)]]
                                                                 : D.groups[D.order[mod(6 * (day - E) + k, N)]]); }}
// a dropped group (no posting allowed) counts as done, so its session can still finish and it shows as a slim note
const isDone = (t, day, g) => g.dropped || !!t[day + "-" + g.name];
function card(g, i, day, enIdx) {{
  const key = day + "-" + g.name, done = !!ticks()[key], pr = pends()[g.name], pendNow = !!(pr && pr.day === day);
  const pendOld = pr && pr.day < day ? pr : null;
  let body;
  // the round this card belongs to (round 0 = 31 Oct–4 Nov, the first one the owner posted): the same video for all groups
  let shown = 0;   // the video index this card shows (logged when ticked Posted)
  if (g.code === "en" || g.share) {{   // share mode: a language group that only lets members share → the English Reel
    shown = videoIdx(g, day, i, D.en.length); const r = D.en.length ? D.en[shown] : null, txt = r && (g.share ? r.local[g.code] : r.text);
    body = r ? `<div class="btns"><a class="btn" href="${{r.url}}" target="_blank" rel="noopener">Open the Reel</a>${{g.share ? ` <span class="file">Share the English Reel (this group allows no uploads)</span>` : ""}}
</div><pre>${{esc(txt)}}</pre><button class="copy">Copy text</button>` : `<p class="none">No English Reel on the page yet.</p>`;
    g._text = txt;
  }} else {{
    const fs = D.files[g.code] || []; shown = videoIdx(g, day, i, fs.length); const f = fs[shown];
    body = f ? `<div class="btns"><span class="file">Upload: <b>${{esc(f.file)}}</b> <span class="meta">(${{esc(f.title)}})</span></span></div><pre>${{esc(f.text)}}</pre><button class="copy">Copy text</button>`
             : `<p class="none">No ${{g.lang}} version yet: skip this one.</p>`;
    g._text = f && f.text;
  }}
  const c = document.createElement("div"); c.className = "card" + (done ? " done" : "");
  c.innerHTML = `<div class="top"><button class="name">Copy name</button>
    ${{g.url ? `<a class="g" href="${{g.url}}" target="_blank" rel="noopener">${{esc(g.name)}}</a>` : `<span class="g">${{esc(g.name)}}</span>`}}
    <span class="right"><button class="pend${{pendNow ? " on" : ""}}" type="button">${{pendNow ? "Pending — skipped" : "Still pending"}}</button><label class="tick"><input type="checkbox" ${{done && !pendNow ? "checked" : ""}}> Posted</label><span class="num">${{i + 1}}</span></span></div>` +
    (pendOld ? `<p class="note">${{pendOld.n >= 2 ? `Still pending ${{pendOld.n}} rounds in a row (last: ${{pendOld.date}}) — slow admins (posts do get approved). Still waiting? Tap Still pending again.`
      : `Your last post here was still waiting for approval (${{pendOld.date}}). Open the group first: if Facebook says a post is pending, tap Still pending.`}}</p>` : "") +
    body.replace('<div class="btns">', `<div class="btns">`).replace("</div><pre>", `<span class="meta">${{g.members}} members <span class="lang ${{g.code}}">${{g.lang}}</span></span></div><div class="box"><pre>`).replace('<button class="copy">Copy text</button>', '<button class="copy">Copy text</button></div>');
  const b = c.querySelector("button.copy"), text = g._text;
  c.querySelector("button.name").onclick = e => navigator.clipboard.writeText(g.name.replace(/ \\(.*\\)$/, "")).then(() => {{ e.target.textContent = "Copied ✓"; setTimeout(() => e.target.textContent = "Copy name", 1500); }});
  if (b) b.onclick = () => navigator.clipboard.writeText(text).then(() => {{ b.textContent = "Copied ✓"; setTimeout(() => b.textContent = "Copy text", 1500); }});
  c.querySelector("input").onchange = e => {{ tick(key, e.target.checked); logSent(key, e.target.checked ? shown : null); if (e.target.checked) setPend(g.name, null); c.classList.toggle("done", e.target.checked); if (i < 3) render(); }};
  c.querySelector("button.pend").onclick = () => {{
    if (pendNow) {{ setPend(g.name, null); tick(key, false); }}                       // tapped by mistake: undo
    else {{ setPend(g.name, {{day, date: ymd(now), n: (pendOld ? pendOld.n : 0) + 1}}); tick(key, true); }}   // counts as done, so the session can finish
    render(); fill("yesterday", dayNo - 1, false);
  }};
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
// the YouTube Post on carousel days (Wed + Sun; owner 2026-11-04): the same pictures + text as the Instagram carousel,
// which Instagram and the Facebook Page get automatically at 19:00. Yesterday's stays until it's ticked.
function ytCard() {{
  const today = ymd(now), yd = new Date(now); yd.setDate(yd.getDate() - 1);
  const p = (D.yt || []).find(p => p.date === today) || (D.yt || []).find(p => p.date === ymd(yd) && !ticks()["yt-" + p.date]);
  if (!p) return null;
  const key = "yt-" + p.date, done = !!ticks()[key], wrap = document.createElement("div");
  wrap.innerHTML = `<h3>YouTube Post${{p.date === today ? "" : " (yesterday's)"}}</h3><div class="card${{done ? " done" : ""}}"><div class="top">
    <span class="g">${{esc(p.title)}}</span><span class="right"><label class="tick"><input type="checkbox" ${{done ? "checked" : ""}}> Posted</label></span></div>
    <div class="btns"><a class="btn" href="https://www.youtube.com/@2MinArabic/posts" target="_blank" rel="noopener">Open YouTube Posts</a>
    <span class="file">Pictures: <b>Downloads → yt-posts → ${{esc(p.folder)}}</b> (all ${{p.n}})</span></div>
    <div class="box"><pre>${{esc(p.text)}}</pre><button class="copy">Copy text</button></div></div>`;
  const b = wrap.querySelector("button.copy");
  b.onclick = () => navigator.clipboard.writeText(p.text).then(() => {{ b.textContent = "Copied ✓"; setTimeout(() => b.textContent = "Copy text", 1500); }});
  wrap.querySelector("input").onchange = e => {{ tick(key, e.target.checked); wrap.querySelector(".card").classList.toggle("done", e.target.checked); }};
  return wrap;
}}
// Facebook to-dos (owner 2026-11-08: "remind me of those to remove"): dropped groups to leave (tick "Left"), groups to test
function todoCard() {{
  let left = {{}}; try {{ left = JSON.parse(localStorage.getItem("fbgl") || "{{}}"); }} catch (e) {{}}
  const leave = D.groups.filter(g => g.dropped && !g.todo && !left[g.name]), test = D.groups.filter(g => g.todo);
  const box = document.getElementById("todo"); box.innerHTML = "";
  if (!leave.length && !test.length) return;
  box.innerHTML = `<h3>Facebook to-dos</h3><div class="card">` +
    (leave.length ? `<p class="meta" style="margin:0 0 6px">Leave these groups (they don't allow our posts) — open → Joined ▾ → Leave group:</p>` +
      leave.map(g => `<label class="tick" style="margin:4px 0"><input type="checkbox" data-n="${{esc(g.name)}}"> ${{esc(g.name)}}</label>`).join("") : "") +
    (test.length ? `<p class="meta" style="margin:${{leave.length ? 12 : 0}}px 0 6px">To check, then tell Claude:</p>` +
      test.map(g => `<p style="margin:4px 0"><b>${{esc(g.name)}}</b> — ${{esc(g.todo)}}</p>`).join("") : "") + `</div>`;
  box.querySelectorAll("input").forEach(i => i.onchange = () => {{ try {{ left[i.dataset.n] = Date.now(); localStorage.setItem("fbgl", JSON.stringify(left)); }} catch (e) {{}} todoCard(); }});
}}
function render() {{ todoCard(); if (document.getElementById("all").innerHTML) allTable(); fill("today", dayNo, true); const y = ytCard(); if (y) document.getElementById("today").prepend(y); }}
// footer: last update + countdown to the next one (site-latest.yml runs hourly at :25, 05–20 UTC)
const UPD = Array.from({{length: 16}}, (_, k) => 5 + k).map(h => h);  // checks at :05 (laptop) and :25 (GitHub)
function footer() {{
  const f = document.getElementById("foot"), built = new Date(f.dataset.built), t = new Date();
  let next = null;
  for (let d = 0; d < 2 && !next; d++) for (const h of UPD) {{
    const c = new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() + d, h, 25));
    if (c > t) {{ next = c; break; }}
  }}
  // owner 2026-11-04: three short lines — "updated: 1:56h ago (4.nov)" / "next hourly check in 22min" / "auto-refreshing page"
  const span = ms => {{ const m = Math.round(Math.abs(ms) / 60000), h = Math.floor(m / 60);
    return h ? `${{h}}:${{String(m % 60).padStart(2, "0")}}h` : `${{m}}min`; }};
  const at = d => d.toLocaleDateString("en-GB", {{timeZone: "Europe/Oslo", day: "numeric"}}) + "."
    + d.toLocaleDateString("en-GB", {{timeZone: "Europe/Oslo", month: "short"}}).toLowerCase();
  f.innerHTML = `updated: ${{span(t - built)}} ago (${{at(built)}})<br>next hourly check in ${{span(next - t)}}<br>auto-refreshing page`;
}}
footer(); setInterval(footer, 60000);
// self-refresh (owner 2026-11-03): every 5 min, only while the page is on screen — the content changes at most hourly
// and GitHub Pages caches it 10 min, so faster gains nothing. A tiny conditional request (304 when unchanged); the
// page reloads only when the content fingerprint changed or the Oslo day turned over. Ticks live in localStorage.
let lastCheck = Date.now();
async function refresh() {{
  if (document.visibilityState !== "visible" || Date.now() - lastCheck < 60000) return;
  lastCheck = Date.now();
  const day = ymd(new Date(new Date().toLocaleString("en-US", {{timeZone: "Europe/Oslo"}})));
  if (day !== ymd(now)) return location.reload();
  try {{
    const r = await fetch(location.pathname, {{cache: "no-cache"}});
    const m = r.ok && (await r.text()).match(/data-fp="([^"]*)"/);
    if (m && m[1] !== document.getElementById("foot").dataset.fp) location.reload();
  }} catch (e) {{}}   // offline: try again next time
}}
setInterval(refresh, 5 * 60000);
document.addEventListener("visibilitychange", refresh);   // back to the tab → check at once
document.getElementById("date").textContent = now.toLocaleDateString("en-GB", {{weekday: "long", day: "numeric", month: "long"}});
render(); setInterval(() => {{ if (document.querySelector(".card.locked")) render(); }}, 60000); fill("yesterday", dayNo - 1, false);
// the table also shows each group's next turn and the video it will get (owner 2026-11-07)
function allTable() {{
  const t = ticks();
  const nextTurn = name => {{
    for (let d = dayNo; d < dayNo + 60; d++) {{
      const k = slots(d).findIndex(x => x.name === name);
      if (k >= 0 && !(d === dayNo && t[d + "-" + name])) return [d, k];
    }}
    return null;
  }};
  const when = d => {{ const x = new Date(now); x.setDate(x.getDate() + d - dayNo);
    return d === dayNo ? "today" : d === dayNo + 1 ? "tomorrow" : x.toLocaleDateString("en-GB", {{weekday: "short", day: "numeric", month: "short"}}); }};
  document.getElementById("all").innerHTML = "<table><tr><th>#</th><th>Group</th><th>Next video</th></tr>" +
    D.order.map((gi, i) => {{
      const g = D.groups[gi]; let next = "—";
      if (g.dropped) next = "dropped";
      else {{
        const nt = nextTurn(g.name), list = g.code === "en" || g.share ? D.en : (D.files[g.code] || []);
        if (nt && list.length) {{ const v = list[videoIdx(g, nt[0], nt[1], list.length)];
          next = `<span class="vt" title="${{esc(v.title)}}">${{esc(v.title)}}</span><span class="meta">${{when(nt[0])}}, ${{nt[1] < 3 ? "morning" : "evening"}}${{pends()[g.name] ? " · was pending" : ""}}</span>`; }}
      }}
      return `<tr><td>${{i + 1}}</td><td><span class="lang ${{g.code}}">${{g.lang}}</span> ${{esc(g.name)}}</td><td>${{next}}</td></tr>`;
    }}).join("") + "</table>";
}}
allTable();
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
    groups = [{"name": n, "code": l, "lang": LANG[l], "members": m, "kind": k, "url": URLS.get(n, ""), "dropped": n in DROPPED, "start": START_IDX.get(n, 0), "share": n in SHARE, "todo": TODO.get(n, "")} for n, l, m, k in GROUPS]
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
