#!/usr/bin/env python3
"""One-off (macOS): turn assets/photo.jpg into two ASCII portraits:
portrait.txt (light theme: dark pixels dense) and portrait_dark.txt (dark theme: bright pixels dense).
Run locally; the Action only reads the .txt files."""
import subprocess, struct, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "assets", "photo.jpg")
COLS, ROWS = 124, 62
bmp = "/tmp/portrait.bmp"
subprocess.run(["sips", "-s", "format", "bmp", "-z", str(ROWS), str(COLS), src, "--out", bmp], check=True, capture_output=True)
b = open(bmp, "rb").read()
off = struct.unpack("<I", b[10:14])[0]; w, h = struct.unpack("<ii", b[18:26]); bpp = struct.unpack("<H", b[28:30])[0] // 8
stride = (w * bpp + 3) // 4 * 4
H = abs(h)
lum = []
for y in range(H):
    row = (H - 1 - y) if h > 0 else y
    base = off + row * stride
    lum.append([0.114 * b[base + x * bpp] + 0.587 * b[base + x * bpp + 1] + 0.299 * b[base + x * bpp + 2] for x in range(w)])
# unsharp mask for crisp edges
def blur(x, y):
    t = n = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < w:
                t += lum[yy][xx]; n += 1
    return t / n
sharp = [[max(0, min(255, lum[y][x] + 1.6 * (lum[y][x] - blur(x, y)))) for x in range(w)] for y in range(H)]
flat = sorted(v for r in sharp for v in r)
lo, hi = flat[int(len(flat) * .02)], flat[int(len(flat) * .50)]
def eq(v):   # 1 = darkest subject, 0 = wall
    return 1 - min(1, max(0, (v - lo) / (hi - lo)))
ramp = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
def render(invert):
    out = []
    for r in sharp:
        s = ""
        for v in r:
            t = eq(v)
            s += ramp[int(min(1, t ** 0.85) * (len(ramp) - 1))] if t > .10 else " "
        out.append(s.rstrip())
    return "\n".join(out)
open(os.path.join(ROOT, "assets", "portrait.txt"), "w").write(render(False))
print(H, "rows x", w, "cols")
