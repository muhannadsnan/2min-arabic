#!/usr/bin/env python3
"""Generate one image through a running ComfyUI server (FLUX.2 [klein] 4B by default).

Start the server first (caller's job), e.g.:
    cd /media/msn/GamesLinux/AI/ComfyUI && venv/bin/python main.py --listen 127.0.0.1 --port 8188 --lowvram
(or /media/msn/GamesLinux/AI/run_comfyui.sh). Stop it afterwards with Ctrl+C / kill.

Usage:
    python3 generate.py "Sami waving on a street" out.png [--seed 7] [--steps 4]
    python3 generate.py "same man now sitting in a cafe" out.png --ref sami.png   # klein reference/edit
    python3 generate.py "..." out.png --workflow workflow-api-zimage.json          # Z-Image Turbo alt
The channel style suffix is appended unless --no-style is given. Stdlib only.
"""
import argparse, json, os, random, sys, time, uuid, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = ("flat vector illustration, warm pastel palette (sand, terracotta, teal, cream), soft shadows, "
         "clean simple shapes, friendly, vertical 9:16 composition, the scene fills the whole frame edge to edge, "
         "simple uncluttered background, no text, no letters, no watermark")
# from Day 6 on (owner, 2026-10-01): 3D animated-movie look — costs the same as flat, animates far better
STYLE_3D = ("3D animated movie style, soft cinematic lighting, expressive stylized characters, Pixar-like but original, "
            "warm palette (sand, terracotta, teal, cream), rich depth, vertical 9:16 composition, the scene fills the "
            "whole frame edge to edge, no text, no letters, no signs, no watermark, "
            "every woman dressed modestly in loose-fitting clothes: long loose skirt or wide loose trousers to the ankle, "
            "loose tops with high necklines, sleeves at least to the elbow, nothing tight, no bare legs, no bare shoulders")
# owner, 2026-10-05: no exposed body parts, no tight jeans or tight tops on women (Arab audience); hijab optional
STYLES = {"flat": STYLE, "3d": STYLE_3D}


def http(server, path, data=None, headers=None):
    req = urllib.request.Request(f"http://{server}{path}", data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def upload(server, path):
    boundary = uuid.uuid4().hex
    name = f"ref_{uuid.uuid4().hex[:8]}_{os.path.basename(path)}"
    with open(path, "rb") as f:
        img = f.read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + img + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    res = json.loads(http(server, "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return res["name"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("output")
    ap.add_argument("--workflow", default=os.path.join(HERE, "workflow-api.json"))
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=1344)
    ap.add_argument("--ref", action="append", default=[], help="reference image(s) (klein workflow only)")
    ap.add_argument("--no-style", action="store_true")
    ap.add_argument("--style", choices=sorted(STYLES), default="flat")
    a = ap.parse_args()

    wf = json.load(open(a.workflow))
    wf["4"]["inputs"]["text"] = a.prompt if a.no_style else f"{a.prompt.rstrip('. ')}. {STYLES[a.style]}"
    seed = a.seed if a.seed is not None else random.randint(0, 2**31)
    for nid, n in wf.items():
        i = n["inputs"]
        if "noise_seed" in i: i["noise_seed"] = seed
        if n["class_type"] == "KSampler": i["seed"] = seed
        if "width" in i: i["width"], i["height"] = a.width, a.height
        if a.steps and "steps" in i: i["steps"] = a.steps

    if a.ref:  # FLUX.2 klein multi-reference: chain ReferenceLatent on both conds
        pos, neg = ["4", 0], ["5", 0]
        for k, path in enumerate(a.ref):
            b = 100 + 10 * k
            wf[str(b)] = {"class_type": "LoadImage", "inputs": {"image": upload(a.server, path)}}
            wf[str(b+1)] = {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": [str(b), 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 16}}
            wf[str(b+2)] = {"class_type": "VAEEncode", "inputs": {"pixels": [str(b+1), 0], "vae": ["3", 0]}}
            wf[str(b+3)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": pos, "latent": [str(b+2), 0]}}
            wf[str(b+4)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": neg, "latent": [str(b+2), 0]}}
            pos, neg = [str(b+3), 0], [str(b+4), 0]
        wf["10"]["inputs"]["positive"], wf["10"]["inputs"]["negative"] = pos, neg

    t0 = time.time()
    pid = json.loads(http(a.server, "/prompt", json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode(),
                          {"Content-Type": "application/json"}))["prompt_id"]
    while True:
        hist = json.loads(http(a.server, f"/history/{pid}"))
        if pid in hist:
            h = hist[pid]
            if h.get("status", {}).get("status_str") == "error":
                sys.exit(f"ComfyUI error: {json.dumps(h['status'], indent=1)[:2000]}")
            if h.get("outputs"):
                break
        time.sleep(1)
    img = next(im for o in h["outputs"].values() for im in o.get("images", []))
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    with open(a.output, "wb") as f:
        f.write(http(a.server, f"/view?{q}"))
    print(f"saved {a.output} seed={seed} {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
