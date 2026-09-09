# -*- coding: utf-8 -*-
"""Slice progress bar: empty track (top) + cyan fill (from bottom)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

SRC = Path(
    r"C:\Users\Administrator\.cursor\projects\d-code-yingie\assets"
    r"\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images"
    r"_1788938860724_d-1f31cdd1-af36-4f01-af0f-422e0a8273ac.png"
)
OUT = Path(r"D:\code_yingie\插件打包工具\tmp")

TARGET_W = 600
TARGET_H = 56


def content_bbox(img: Image.Image, thr: int = 22):
    px = img.load()
    iw, ih = img.size
    xs, ys = [], []
    for y in range(ih):
        for x in range(iw):
            r, g, b, a = px[x, y]
            if a > 8 and (r + g + b) > thr * 3:
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, iw, ih)
    pad = 2
    return (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(iw, max(xs) + 1 + pad),
        min(ih, max(ys) + 1 + pad),
    )


def is_cyan(r, g, b, a=255) -> bool:
    if a < 20:
        return False
    return g > 60 and b > 60 and (g + b) > 160 and (g + b - 2 * r) > 30


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    mid = h // 2
    top = im.crop((0, 0, w, mid))
    bot = im.crop((0, mid, w, h))

    track = top.crop(content_bbox(top))
    filled = bot.crop(content_bbox(bot))
    print("raw", track.size, filled.size)

    bg = track.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    filled_s = filled.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)

    # Measure cyan band / insets from filled art
    px = filled_s.load()
    cyan_ys, cyan_xs = [], []
    for y in range(TARGET_H):
        for x in range(TARGET_W):
            r, g, b, a = px[x, y]
            if is_cyan(r, g, b, a):
                cyan_ys.append(y)
                cyan_xs.append(x)
    if not cyan_xs:
        inset_l, inset_r = 18, TARGET_W - 18
        y0, y1 = 14, TARGET_H - 14
    else:
        inset_l, inset_r = min(cyan_xs), max(cyan_xs) + 1
        y0, y1 = min(cyan_ys), max(cyan_ys) + 1
    print("cyan box", inset_l, y0, inset_r, y1)

    # Sample clean cyan from left third (avoid center text)
    sx0 = inset_l + 4
    sx1 = min(inset_r, inset_l + max(24, int((inset_r - inset_l) * 0.22)))
    sample = filled_s.crop((sx0, y0, sx1, y1))

    # If sample weak, synthesize glossy teal
    sc = 0
    sp = sample.load()
    for yy in range(sample.height):
        for xx in range(sample.width):
            r, g, b, a = sp[xx, yy]
            if is_cyan(r, g, b, a):
                sc += 1
    if sc < sample.width * sample.height * 0.25:
        sample = Image.new("RGBA", (40, max(1, y1 - y0)))
        d = ImageDraw.Draw(sample)
        for i in range(sample.height):
            t = i / max(1, sample.height - 1)
            d.line(
                [(0, i), (sample.width, i)],
                fill=(
                    int(10 + 30 * (1 - abs(t - 0.35))),
                    int(140 + 70 * (1 - abs(t - 0.35))),
                    int(155 + 70 * (1 - abs(t - 0.35))),
                    255,
                ),
            )

    fill_w = max(1, inset_r - inset_l)
    tiled = Image.new("RGBA", (fill_w, y1 - y0))
    x = 0
    while x < fill_w:
        tiled.paste(sample, (x, 0))
        x += sample.width
    tiled = tiled.crop((0, 0, fill_w, y1 - y0))
    tiled = ImageEnhance.Brightness(tiled).enhance(1.1)
    tiled = ImageEnhance.Color(tiled).enhance(1.15)

    fg = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    fg.paste(tiled, (inset_l, y0), tiled)

    bg.save(OUT / "progressbar_background.png")
    fg.save(OUT / "progressbar_foreground.png")
    print("saved", bg.size, fg.size)

    # composite preview at 75%
    prev = bg.copy()
    clip = fg.crop((0, 0, int(TARGET_W * 0.75), TARGET_H))
    prev.paste(clip, (0, 0), clip)
    prev.save(OUT / "_pb_preview_75.png")


if __name__ == "__main__":
    main()
