#!/usr/bin/env python3
"""Queue dubbed Trial Reels (owner, 2026-10-19): a top video's dubbed versions, one language a day, for non-followers.

    python3 tools/ig_trial_add.py <stem> output/ig-trial/captions-<stem>.json [--apply]

captions json: [{"lang": "tr", "audio": "tr", "caption": "…"}, …] in posting order (Urdu uses the Hindi audio, Malay the
Indonesian). Video = output/<stem>/dub-<audio>-preview.mp4, cover = the video's thumbnail. Each bundle is encrypted
with the Instagram queue key (like the main queue) and uploaded to the `ig-trial` release as trial-NN-<lang>.bin,
numbered after what's already queued. The workflow instagram-trial.yml posts one a day.
"""
import json, pathlib, re, subprocess, sys, tempfile, shutil
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = pathlib.Path.home() / ".config/2min-instagram/queue.key"; REPO, Q = "muhannadsnan/2min-arabic", "ig-trial"

def main():
    stem, cap_file = sys.argv[1], sys.argv[2]; apply = "--apply" in sys.argv
    items = json.loads(pathlib.Path(cap_file).read_text(encoding="utf-8"))
    thumb = next(p for p in (ROOT / "output" / stem).glob("*thumbnail.jpg"))
    r = subprocess.run(["gh", "release", "view", Q, "-R", REPO, "--json", "assets", "--jq", ".assets[].name"], capture_output=True, text=True)
    if r.returncode != 0 and apply:
        subprocess.run(["gh", "release", "create", Q, "-R", REPO, "--title", "Instagram trial queue (encrypted)",
                        "--notes", "Encrypted dubbed Trial Reels, one a day (tools/ig_trial_add.py)."], check=True)
        existing = []
    else:
        existing = [int(m.group(1)) for m in re.finditer(r"trial-(\d+)-", r.stdout)] if r.returncode == 0 else []
    n0 = max(existing, default=0); tmp = pathlib.Path(tempfile.mkdtemp()); built = []
    for i, it in enumerate(items, 1):
        w = tmp / f"w{i}"; w.mkdir()
        video = ROOT / "output" / stem / f"dub-{it['audio']}-preview.mp4"
        if not video.exists(): sys.exit(f"missing {video}")
        shutil.copy(video, w / "video.mp4"); shutil.copy(thumb, w / "cover.jpg")
        (w / "caption.txt").write_text(it["caption"].strip() + "\n", encoding="utf-8")
        if len(it["caption"]) > 2200: sys.exit(f"{it['lang']}: caption too long")
        b = tmp / f"trial-{n0 + i:02d}-{it['lang']}.bin"
        subprocess.run(f'tar -C "{w}" -cf - video.mp4 cover.jpg caption.txt | '
                       f'openssl enc -aes-256-cbc -pbkdf2 -salt -pass file:"{KEY}" -out "{b}"', shell=True, check=True)
        built.append(b); print(f"{b.name}  {video.name}  {it['caption'].splitlines()[0][:60]}")
    if apply:
        subprocess.run(["gh", "release", "upload", Q, "-R", REPO, *map(str, built)], check=True)
        print(f"queued {len(built)} Trial Reels")
    else:
        print("dry run — add --apply to upload")

if __name__ == "__main__":
    main()
