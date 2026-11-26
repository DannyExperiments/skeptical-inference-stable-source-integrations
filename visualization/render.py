#!/usr/bin/env python3
"""Illustrate the two marker branches and repair table in three dimensions."""
from itertools import combinations, product
from math import cos, pi, sin, tau
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 664, 434
COLORS = ["#0d1825", "#16273a", "#2b445a", "#edf5fb", "#b0c6d9", "#83e2ce", "#ffc179", "#6b95ae"]
VERTICES = list(product((0, 1), repeat=3))
EDGES = [(a, b) for a, b in combinations(VERTICES, 2) if sum(x != y for x, y in zip(a, b)) == 1]


def font(size, bold=False):
    names = ("Arial Bold.ttf", "DejaVuSans-Bold.ttf") if bold else ("Arial.ttf", "DejaVuSans.ttf")
    for name in names:
        for path in (Path("/System/Library/Fonts/Supplemental") / name,
                     Path("/usr/share/fonts/truetype/dejavu") / name):
            if path.is_file():
                return ImageFont.truetype(str(path), size)
    raise RuntimeError("Arial or DejaVu Sans is required")


FONTS = [font(32, True), font(19), font(22, True), font(18), font(19, True)]


def project(point, angle):
    x, y, z = (u-.5 for u in point)
    x, z = x*cos(angle)+z*sin(angle), -x*sin(angle)+z*cos(angle)
    y, z = y*cos(.38)-z*sin(.38), y*sin(.38)+z*cos(.38)
    scale = 137*5/(5-z)
    return 188+x*scale, 207-y*scale, z


def frame(angle, complete):
    image = Image.new("RGB", (W, H), COLORS[0])
    d = ImageDraw.Draw(image)
    d.text((24, 18), "One stable branch is guaranteed", font=FONTS[0], fill=COLORS[3])
    d.text((24, 59), "A marker separates stability from skeptical entailment", font=FONTS[1], fill=COLORS[4])
    d.rounded_rectangle((24, 102, 353, 353), radius=18, fill=COLORS[1], outline=COLORS[2])
    d.rounded_rectangle((365, 102, 640, 353), radius=18, fill=COLORS[1], outline=COLORS[2])
    p = {point: project(point, angle) for point in VERTICES}
    for a, b in sorted(EDGES, key=lambda e:p[e[0]][2]+p[e[1]][2]):
        color = COLORS[7 if p[a][2]+p[b][2] > 0 else 2]
        d.line((*p[a][:2], *p[b][:2]), fill=color, width=2)
    for (q, y, t), (x, ypx, _) in sorted(p.items(), key=lambda item:item[1][2]):
        good = q == 1 or complete or y or t
        color = COLORS[7 if q else 5 if good else 6]
        if not good:
            d.ellipse((x-11, ypx-11, x+11, ypx+11), fill=COLORS[1], outline=color, width=2)
        d.ellipse((x-6, ypx-6, x+6, ypx+6), fill=color, outline=COLORS[1], width=1)
    d.text((39, 323), "Cube coordinates  (q, y, t)", font=FONTS[3], fill=COLORS[4])
    d.text((384, 119), "q = 1 always stable", font=FONTS[2], fill=COLORS[7])
    d.text((384, 161), "q = 0 branch", font=FONTS[4], fill=COLORS[3])
    if complete:
        d.text((384, 197), "All four repairs exist.", font=FONTS[3], fill=COLORS[5])
        d.text((384, 228), "A false-marker order survives.", font=FONTS[3], fill=COLORS[3])
        d.text((384, 289), "Query q is not entailed", font=FONTS[2], fill=COLORS[6])
    else:
        d.text((384, 197), "No repair at y = t = 0.", font=FONTS[3], fill=COLORS[6])
        d.text((384, 228), "Only the fallback survives.", font=FONTS[3], fill=COLORS[3])
        d.text((384, 289), "Query q is entailed", font=FONTS[2], fill=COLORS[5])
    d.text((24, 368), "Blue: fallback    ·    Mint: repair exists    ·    Amber: blocked", font=FONTS[3], fill=COLORS[4])
    d.text((24, 401), "Worked slice: x = 0, s = 1. The paper proves the general result.", font=FONTS[4], fill=COLORS[3])
    return image


def main():
    palette = Image.new("P", (1, 1))
    palette.putpalette([int(c[i:i+2],16) for c in COLORS for i in (1,3,5)] + [0,0,0]*(256-len(COLORS)))
    frames = [frame(tau*i/48 + pi/7, i<24).quantize(palette=palette,dither=Image.Dither.NONE) for i in range(48)]
    frames[0].save(Path(__file__).with_name("stable-marker-branches.gif"), save_all=True, append_images=frames[1:],
                   loop=0, duration=135, optimize=True, disposal=1)


if __name__ == "__main__":
    main()
