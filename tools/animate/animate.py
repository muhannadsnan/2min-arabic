#!/usr/bin/env python3
"""Image-to-video test for the "animated scroll-stopper" (Wan 2.2 TI2V-5B GGUF, via a running ComfyUI).

Stdlib only. Measures wall-clock time, peak GPU memory (nvidia-smi), lowest free RAM and swap traffic.

    python3 animate.py IMAGE OUT.mp4 --prompt "..." [--width 480 --height 832 --frames 73 --fps 24 --steps 20 --seed 1]
"""
import argparse, json, os, random, subprocess, sys, threading, time, uuid, urllib.request, urllib.parse

NEG = ("色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，"
       "多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走, "
       "photorealistic, 3d render, text, watermark, extra fingers, deformed hands, distorted face")


def http(server, path, data=None, headers=None):
    req = urllib.request.Request(f"http://{server}{path}", data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def upload(server, path):
    b = uuid.uuid4().hex
    name = f"i2v_{uuid.uuid4().hex[:8]}_{os.path.basename(path)}"
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + open(path, "rb").read() + \
           f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return json.loads(http(server, "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"}))["name"]


def workflow(a, image_name, seed):
    return {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": a.unet}},
        "2": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": a.clip, "type": "wan"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": a.prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
        "6": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "7": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"vae": ["3", 0], "width": a.width, "height": a.height,
              "length": a.frames, "batch_size": 1, "start_image": ["6", 0]}},
        "8": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": a.shift}},
        "9": {"class_type": "KSampler", "inputs": {"model": ["8", 0], "seed": seed, "steps": a.steps, "cfg": a.cfg,
              "sampler_name": "uni_pc", "scheduler": "simple", "positive": ["4", 0], "negative": ["5", 0],
              "latent_image": ["7", 0], "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
        "11": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "fps": a.fps}},
        "12": {"class_type": "SaveVideo", "inputs": {"video": ["11", 0], "filename_prefix": "video/scrollstopper",
               "format": "auto", "codec": "auto"}},
    }


class Meter(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.peak_vram = 0; self.min_avail = 10**12; self.stop = False
        self.swap0 = self.swap()

    @staticmethod
    def swap():
        d = dict(l.split() for l in open("/proc/vmstat") if l.startswith(("pswpin", "pswpout")))
        return int(d["pswpin"]), int(d["pswpout"])

    def run(self):
        while not self.stop:
            try:
                v = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]).split()[0])
                self.peak_vram = max(self.peak_vram, v)
                m = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
                self.min_avail = min(self.min_avail, m["MemAvailable"] // 1024)
            except Exception:
                pass
            time.sleep(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("output")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--unet", default="Wan2.2-TI2V-5B-Q5_K_M.gguf")
    ap.add_argument("--clip", default="umt5-xxl-encoder-Q5_K_M.gguf")
    ap.add_argument("--width", type=int, default=480); ap.add_argument("--height", type=int, default=832)
    ap.add_argument("--frames", type=int, default=73); ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--steps", type=int, default=20); ap.add_argument("--cfg", type=float, default=5.0)
    ap.add_argument("--shift", type=float, default=8.0)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    seed = a.seed if a.seed is not None else random.randint(0, 2**31)
    meter = Meter(); meter.start()
    t0 = time.time()
    wf = workflow(a, upload(a.server, a.image), seed)
    pid = json.loads(http(a.server, "/prompt", json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode(),
                          {"Content-Type": "application/json"}))["prompt_id"]
    while True:
        hist = json.loads(http(a.server, f"/history/{pid}"))
        if pid in hist:
            h = hist[pid]
            if h.get("status", {}).get("status_str") == "error":
                meter.stop = True
                sys.exit(f"ComfyUI error: {json.dumps(h['status'], indent=1)[-3000:]}")
            if h.get("outputs"):
                break
        time.sleep(2)
    dt = time.time() - t0
    meter.stop = True
    vid = next(f for o in h["outputs"].values() for k, v in o.items() if isinstance(v, list)
               for f in v if isinstance(f, dict) and f.get("filename", "").endswith((".mp4", ".webm")))
    q = urllib.parse.urlencode({"filename": vid["filename"], "subfolder": vid["subfolder"], "type": vid["type"]})
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    open(a.output, "wb").write(http(a.server, f"/view?{q}"))
    s1 = meter.swap()
    res = {"output": a.output, "seed": seed, "width": a.width, "height": a.height, "frames": a.frames, "fps": a.fps,
           "steps": a.steps, "unet": a.unet, "clip": a.clip, "seconds": round(dt, 1), "peak_vram_mb": meter.peak_vram,
           "min_ram_available_mb": meter.min_avail, "swap_in_pages": s1[0] - meter.swap0[0],
           "swap_out_pages": s1[1] - meter.swap0[1], "prompt": a.prompt}
    print(json.dumps(res))
    with open(os.path.join(os.path.dirname(os.path.abspath(a.output)), "runs.jsonl"), "a") as f:
        f.write(json.dumps(res) + "\n")


if __name__ == "__main__":
    main()
