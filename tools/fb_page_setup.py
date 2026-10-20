#!/usr/bin/env python3
"""One-time setup for posting the daily Reel to the Facebook Page "2 Minute Arabic" too (owner, 2026-10-20).

    python3 tools/fb_page_setup.py [--from-file ~/Downloads/accesstoken.txt]

Paste the LONG-LIVED user token from Graph API Explorer → Access Token Debugger → "Extend Access Token" when asked
(input is hidden, never shown or logged). The script asks Facebook for the Page's own token — a Page token made from a
long-lived user token does not expire — saves it to ~/.config/2min-facebook/page.json (mode 600) and sets the GitHub
secrets FB_PAGE_ID and FB_PAGE_TOKEN (piped, never printed). The user token itself is not stored.
"""
import getpass, json, pathlib, subprocess, sys, urllib.parse, urllib.request

GRAPH = "https://graph.facebook.com/v21.0"
REPO = "muhannadsnan/2min-arabic"
PAGE_NAME = "2 Minute Arabic"


def get(path, **q):
    with urllib.request.urlopen(f"{GRAPH}/{path}?" + urllib.parse.urlencode(q), timeout=30) as r:
        return json.load(r)


def main():
    if "--from-file" in sys.argv:   # the owner saved the token in a file (never printed; delete the file afterwards)
        import re
        raw = pathlib.Path(sys.argv[sys.argv.index("--from-file") + 1]).expanduser().read_text(errors="ignore")
        m = re.search(r"EAA[A-Za-z0-9]{60,}", raw); user = m.group(0) if m else ""
    else:
        user = getpass.getpass("Paste the long-lived user token (hidden), then Enter: ").strip()
    dbg = get("debug_token", input_token=user, access_token=user).get("data", {}) if len(user) >= 50 else {}
    if dbg.get("expires_at", 0) and dbg["expires_at"] - __import__("time").time() < 7 * 86400:
        sys.exit("This token is short-lived — extend it first (Access Token Tool → Extend Access Token).")
    if "pages_manage_posts" not in dbg.get("scopes", []):
        sys.exit("The token lacks pages_manage_posts — add it in Graph API Explorer and generate again.")
    if len(user) < 50:
        sys.exit("That doesn't look like a token (too short) — nothing saved.")
    pages = get("me/accounts", access_token=user, fields="id,name,access_token,tasks").get("data", [])
    page = next((p for p in pages if p["name"].strip().lower() == PAGE_NAME.lower()), None)
    if not page:
        sys.exit(f"No Page named '{PAGE_NAME}' in this token (found: {[p['name'] for p in pages]}). "
                 "Tick the Page when Graph API Explorer asks which Pages to allow.")
    missing = {"CREATE_CONTENT"} - set(page.get("tasks", []))
    if missing:
        sys.exit(f"The token can't post to the Page (missing {missing}) — add pages_manage_posts and try again.")
    check = get(page["id"], access_token=page["access_token"], fields="name")
    conf = pathlib.Path.home() / ".config/2min-facebook"; conf.mkdir(parents=True, exist_ok=True)
    f = conf / "page.json"
    f.write_text(json.dumps({"page_id": page["id"], "page_name": check["name"], "page_token": page["access_token"]}))
    f.chmod(0o600)
    for name, value in (("FB_PAGE_ID", page["id"]), ("FB_PAGE_TOKEN", page["access_token"])):
        subprocess.run(["gh", "secret", "set", name, "-R", REPO], input=value, text=True, check=True, capture_output=True)
    print(f"✅ Page '{check['name']}' ({page['id']}) saved to {f} and to the GitHub secrets FB_PAGE_ID / FB_PAGE_TOKEN.")


if __name__ == "__main__":
    main()
