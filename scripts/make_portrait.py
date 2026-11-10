#!/usr/bin/env python3
"""One-off (macOS): turn assets/photo.jpg into assets/portrait.txt (ASCII rows).
Run locally; the daily Action only reads portrait.txt."""
import subprocess, struct, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "assets", "photo.jpg")
COLS, ROWS = 84, 42
bmp = "/tmp/portrait.bmp"
subprocess.run(["sips", "-s", "format", "bmp", "-z", str(ROWS), str(COLS), src, "--out", bmp], check=True, capture_output=True)
b = open(bmp, "rb").read()
off = struct.unpack("<I", b[10:14])[0]; w, h = struct.unpack("<ii", b[18:26]); bpp = struct.unpack("<H", b[28:30])[0] // 8
stride = (w * bpp + 3) // 4 * 4
lum = []
for y in range(abs(h)):
    row = (abs(h) - 1 - y) if h > 0 else y
    base = off + row * stride
    lum.append([0.114 * b[base + x * bpp] + 0.587 * b[base + x * bpp + 1] + 0.299 * b[base + x * bpp + 2] for x in range(w)])
flat = sorted(v for r in lum for v in r)
lo, hi = flat[int(len(flat) * .03)], flat[int(len(flat) * .62)]
ramp = " .'`^:;~+*cxo#%@"
out = []
for r in lum:
    s = ""
    for v in r:
        t = 1 - min(1, max(0, (v - lo) / (hi - lo)))
        s += ramp[int(t ** 1.0 * (len(ramp) - 1) if t > .10 else 0)]
    out.append(s.rstrip())
open(os.path.join(ROOT, "assets", "portrait.txt"), "w").write("\n".join(out))
print(len(out), "rows")
