# -*- coding: utf-8 -*-
"""
Carefully rebuild installer assets from the latest UI mockup.
- Clean backgrounds (no black holes / no leftover panels)
- Tight button crops (no neighbor edges)
- Proper 4-state strips
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(r"D:\code_yingie\插件打包工具\tmp")
SRC_UI = ROOT / "_src_ui.png"
SRC_PB = ROOT / "_src_pb.png"
OUT = ROOT
PROBE = ROOT / "probe_clean"
PROBE.mkdir(exist_ok=True)

UI_W, UI_H = 720, 400
BTN_INSTALL_W, BTN_FINISH_W, BTN_H = 200, 140, 44
BTN_CLOSE = 28
PB_W, PB_H = 600, 56

# Tight boxes on 1024x479 mockup (verified iteratively)
BOX = {
    "header": (200, 5, 820, 78),
    "chassis_metal": (70, 250, 960, 310),  # brushed metal strip only
    "left_done": (90, 108, 485, 245),
    "right_vst": (512, 105, 942, 255),
    "btn_finish": (105, 350, 220, 392),
    "btn_install": (280, 350, 465, 392),
    "btn_install_dark": (280, 405, 465, 448),
    "floor": (0, 320, 1024, 479),
    "honey": (0, 0, 1024, 90),
}


def save_probe(name: str, im: Image.Image):
    im.save(PROBE / f"{name}.png")


def make_states(normal: Image.Image, disabled: Image.Image | None = None) -> Image.Image:
    n = normal.convert("RGBA")
    hov = ImageEnhance.Brightness(n).enhance(1.12)
    press = ImageEnhance.Brightness(n).enhance(0.78)
    if disabled is not None:
        dis = disabled.convert("RGBA").resize(n.size, Image.Resampling.LANCZOS)
    else:
        g = ImageOps.grayscale(n).convert("RGBA")
        dis = ImageEnhance.Brightness(g).enhance(0.5)
    strip = Image.new("RGBA", (n.width, n.height * 4))
    for i, fr in enumerate((n, hov, press, dis)):
        strip.paste(fr, (0, i * n.height))
    return strip


def make_close(metal: Image.Image) -> Image.Image:
    s = BTN_CLOSE
    frames = []
    for kind in ("n", "h", "p", "d"):
        base = metal.resize((s, s), Image.Resampling.LANCZOS).convert("RGBA")
        if kind == "h":
            base = ImageEnhance.Brightness(base).enhance(1.25)
        elif kind == "p":
            base = ImageEnhance.Brightness(base).enhance(0.7)
        elif kind == "d":
            base = ImageEnhance.Brightness(base).enhance(0.45)
        d = ImageDraw.Draw(base)
        d.rectangle([0, 0, s - 1, s - 1], outline=(200, 175, 110, 255))
        d.rectangle([1, 1, s - 2, s - 2], outline=(40, 35, 28, 230))
        ink = (235, 235, 235, 255) if kind != "d" else (110, 110, 110, 255)
        m = 8
        d.line([(m, m), (s - 1 - m, s - 1 - m)], fill=ink, width=2)
        d.line([(s - 1 - m, m), (m, s - 1 - m)], fill=ink, width=2)
        frames.append(base)
    strip = Image.new("RGBA", (s, s * 4))
    for i, fr in enumerate(frames):
        strip.paste(fr, (0, i * s))
    return strip


def rivet(d: ImageDraw.ImageDraw, cx: int, cy: int):
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(175, 145, 75), outline=(80, 60, 30))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(95, 75, 35))


def compose_bg(honey: Image.Image, metal: Image.Image, floor: Image.Image, hero: Image.Image, mode: str) -> Image.Image:
    canvas = Image.new("RGB", (UI_W, UI_H), (12, 11, 10))
    # floor
    fl = ImageEnhance.Brightness(floor.resize((UI_W, UI_H), Image.Resampling.LANCZOS)).enhance(0.45)
    canvas.paste(fl, (0, 0))
    # dark veil
    veil = Image.new("RGBA", (UI_W, UI_H), (0, 0, 0, 70))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), veil).convert("RGB")

    # header honeycomb band
    hdr = honey.resize((UI_W, 72), Image.Resampling.LANCZOS)
    canvas.paste(hdr, (0, 0))

    # chassis body from brushed metal only (no dual panels baked in)
    margin = 32
    top_y = 78
    cw, ch = UI_W - margin * 2, UI_H - top_y - 16
    body = Image.new("RGB", (cw, ch), (40, 38, 35))
    metal_big = metal.resize((cw, ch), Image.Resampling.LANCZOS).convert("RGB")
    # tile metal vertically for more natural look
    body = Image.blend(body, metal_big, 0.9)

    # hero well (upper)
    pad = 16
    well_h = ch - 118
    well_w = cw - pad * 2
    well = Image.new("RGB", (well_w, well_h), (16, 14, 13))
    # subtle inner metal rim
    wd = ImageDraw.Draw(well)
    wd.rectangle([0, 0, well_w - 1, well_h - 1], outline=(70, 65, 55))

    hero_img = ImageOps.contain(hero.convert("RGB"), (well_w - 20, well_h - 20))
    if mode == "installing":
        hero_img = ImageEnhance.Brightness(hero_img).enhance(0.4)
        hero_img = ImageEnhance.Color(hero_img).enhance(0.55)
    hx = (well_w - hero_img.width) // 2
    hy = (well_h - hero_img.height) // 2
    well.paste(hero_img, (hx, hy))
    body.paste(well, (pad, 12))

    # lower control deck — dark brushed metal, CLEAR for overlays
    deck = metal.resize((cw - 8, 100), Image.Resampling.LANCZOS).convert("RGB")
    deck = ImageEnhance.Brightness(deck).enhance(0.32)
    body.paste(deck, (4, ch - 104))

    # gold rim + rivets
    rim_w, rim_h = cw + 10, ch + 10
    rim = Image.new("RGB", (rim_w, rim_h), (90, 75, 42))
    rd = ImageDraw.Draw(rim)
    rd.rectangle([0, 0, rim_w - 1, rim_h - 1], outline=(185, 155, 85))
    rd.rectangle([1, 1, rim_w - 2, rim_h - 2], outline=(50, 40, 22))
    rim.paste(body, (5, 5))
    for cx, cy in ((11, 11), (rim_w - 12, 11), (11, rim_h - 12), (rim_w - 12, rim_h - 12)):
        rivet(rd, cx, cy)

    canvas.paste(rim, ((UI_W - rim_w) // 2, top_y))
    return canvas


def rebuild_progress():
    if not SRC_PB.exists():
        print("no progress source, skip")
        return
    im = Image.open(SRC_PB).convert("RGBA")
    w, h = im.size
    mid = h // 2
    top = im.crop((0, 0, w, mid))
    bot = im.crop((0, mid, w, h))

    def bbox(img, thr=20):
        px = img.load()
        xs, ys = [], []
        iw, ih = img.size
        for y in range(ih):
            for x in range(iw):
                r, g, b, a = px[x, y]
                if a > 10 and r + g + b > thr * 3:
                    xs.append(x)
                    ys.append(y)
        return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)

    track = top.crop(bbox(top)).resize((PB_W, PB_H), Image.Resampling.LANCZOS)
    filled = bot.crop(bbox(bot)).resize((PB_W, PB_H), Image.Resampling.LANCZOS)

    def is_cyan(r, g, b, a=255):
        return a > 20 and g > 55 and b > 55 and (g + b) > 150 and (g + b - 2 * r) > 25

    px = filled.load()
    ys, xs = [], []
    for y in range(PB_H):
        for x in range(PB_W):
            r, g, b, a = px[x, y]
            if is_cyan(r, g, b, a):
                ys.append(y)
                xs.append(x)
    if xs:
        x0, x1 = min(xs), max(xs) + 1
        y0, y1 = min(ys), max(ys) + 1
    else:
        x0, x1, y0, y1 = 16, PB_W - 16, 12, PB_H - 12

    # continuous fill: sample a narrow clean band from LEFT of fill (no text, no orange tip repeat)
    sx0 = x0 + int((x1 - x0) * 0.15)
    sx1 = x0 + int((x1 - x0) * 0.28)
    sample = filled.crop((sx0, y0, sx1, y1))
    # strip orange tip from sample left if present
    sp = sample.load()
    for yy in range(sample.height):
        for xx in range(min(6, sample.width)):
            r, g, b, a = sp[xx, yy]
            if r > 120 and r > g and r > b:
                # replace orange with nearby cyan
                sp[xx, yy] = sample.getpixel((min(sample.width - 1, xx + 8), yy))

    fill_w = x1 - x0
    tiled = Image.new("RGBA", (fill_w, y1 - y0))
    x = 0
    while x < fill_w:
        tiled.paste(sample, (x, 0))
        x += sample.width
    tiled = tiled.crop((0, 0, fill_w, y1 - y0))
    tiled = ImageEnhance.Color(tiled).enhance(1.1)
    tiled = ImageEnhance.Brightness(tiled).enhance(1.05)

    fg = Image.new("RGBA", (PB_W, PB_H), (0, 0, 0, 0))
    fg.paste(tiled, (x0, y0), tiled)

    track.convert("RGBA").save(OUT / "progressbar_background.png")
    fg.save(OUT / "progressbar_foreground.png")
    save_probe("pb_bg", track)
    save_probe("pb_fg", fg)
    prev = track.convert("RGBA")
    clip = fg.crop((0, 0, int(PB_W * 0.6), PB_H))
    prev.paste(clip, (0, 0), clip)
    save_probe("pb_preview60", prev)
    print("progress", track.size)


def main():
    ui = Image.open(SRC_UI).convert("RGB")
    print("ui", ui.size)

    # extract pieces
    pieces = {k: ui.crop(v) for k, v in BOX.items()}
    for k, im in pieces.items():
        save_probe(f"src_{k}", im)
        print("crop", k, im.size)

    # buttons — trim neighbor edges: install already starts at 270
    btn_i = pieces["btn_install"].resize((BTN_INSTALL_W, BTN_H), Image.Resampling.LANCZOS)
    btn_id = pieces["btn_install_dark"].resize((BTN_INSTALL_W, BTN_H), Image.Resampling.LANCZOS)
    btn_f = pieces["btn_finish"].resize((BTN_FINISH_W, BTN_H), Image.Resampling.LANCZOS)
    # no dedicated dark finish in sheet — synthesize
    btn_fd = ImageEnhance.Brightness(ImageOps.grayscale(btn_f).convert("RGBA")).enhance(0.55)
    btn_fd = ImageEnhance.Color(btn_fd).enhance(0.15)

    make_states(btn_i, btn_id).save(OUT / "button_setup_or_next.png")
    make_states(btn_f, btn_fd).save(OUT / "button_finish.png")
    make_close(pieces["chassis_metal"]).save(OUT / "button_close.png")
    save_probe("btn_install_strip", Image.open(OUT / "button_setup_or_next.png"))
    save_probe("btn_finish_strip", Image.open(OUT / "button_finish.png"))

    # heroes — slightly tighter already
    left = pieces["left_done"]
    right = pieces["right_vst"]
    honey = pieces["honey"]
    metal = pieces["chassis_metal"]
    floor = pieces["floor"]

    compose_bg(honey, metal, floor, right, "welcome").save(OUT / "background_welcome.png")
    compose_bg(honey, metal, floor, right, "installing").save(OUT / "background_installing.png")
    compose_bg(honey, metal, floor, left, "finish").save(OUT / "background_finish.png")

    save_probe("bg_welcome", Image.open(OUT / "background_welcome.png"))
    save_probe("bg_installing", Image.open(OUT / "background_installing.png"))
    save_probe("bg_finish", Image.open(OUT / "background_finish.png"))

    rebuild_progress()

    for name in (
        "background_welcome.png",
        "background_installing.png",
        "background_finish.png",
        "button_setup_or_next.png",
        "button_finish.png",
        "button_close.png",
        "progressbar_background.png",
        "progressbar_foreground.png",
    ):
        with Image.open(OUT / name) as im:
            print(f"OK {name} {im.size}")


if __name__ == "__main__":
    main()
