# -*- coding: utf-8 -*-
"""Crop industrial-metal installer assets from design mockup (fixed boxes)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

SRC = Path(
    r"C:\Users\Administrator\.cursor\projects\d-code-yingie\assets"
    r"\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images"
    r"_1788938253179_d-84c3cb79-c55d-4c2a-b0bc-480b514ac33e.png"
)
OUT = Path(r"D:\code_yingie\插件打包工具\tmp")

UI_W, UI_H = 720, 400
BTN_H = 44
BTN_INSTALL_W = 200
BTN_FINISH_W = 140
BTN_CLOSE_SIZE = 28
PB_W, PB_H = 640, 12

# Tuned from mockup 1024x479
BOX_HEADER = (0, 0, 1024, 86)
BOX_LEFT = (88, 108, 495, 238)
BOX_RIGHT = (510, 100, 948, 252)
BOX_METAL = (90, 250, 500, 330)
BOX_FLOOR = (0, 300, 1024, 479)
BOX_FINISH = (95, 342, 228, 396)
BOX_INSTALL = (255, 342, 475, 396)
BOX_FINISH_DARK = (95, 400, 228, 454)
BOX_INSTALL_DARK = (255, 400, 475, 454)


def make_states(btn: Image.Image, dark: Image.Image | None = None) -> Image.Image:
    normal = btn.convert("RGBA")
    hover = ImageEnhance.Brightness(normal).enhance(1.14)
    pressed = ImageEnhance.Brightness(normal).enhance(0.78)
    if dark is not None:
        disabled = dark.convert("RGBA").resize(normal.size, Image.Resampling.LANCZOS)
    else:
        g = ImageOps.grayscale(normal).convert("RGBA")
        disabled = ImageEnhance.Brightness(g).enhance(0.55)
    strip = Image.new("RGBA", (normal.width, normal.height * 4))
    for i, frame in enumerate((normal, hover, pressed, disabled)):
        strip.paste(frame, (0, i * normal.height))
    return strip


def make_close_strip(metal_sample: Image.Image) -> Image.Image:
    s = BTN_CLOSE_SIZE
    frames = []
    for kind in ("normal", "hover", "pressed", "disabled"):
        base = metal_sample.resize((s, s), Image.Resampling.LANCZOS).convert("RGBA")
        if kind == "hover":
            base = ImageEnhance.Brightness(base).enhance(1.3)
        elif kind == "pressed":
            base = ImageEnhance.Brightness(base).enhance(0.7)
        elif kind == "disabled":
            base = ImageEnhance.Brightness(base).enhance(0.45)
        d = ImageDraw.Draw(base)
        d.rectangle([0, 0, s - 1, s - 1], outline=(190, 175, 120, 255))
        d.rectangle([1, 1, s - 2, s - 2], outline=(40, 36, 30, 220))
        ink = (230, 230, 230, 255) if kind != "disabled" else (110, 110, 110, 255)
        m = 8
        d.line([(m, m), (s - 1 - m, s - 1 - m)], fill=ink, width=2)
        d.line([(s - 1 - m, m), (m, s - 1 - m)], fill=ink, width=2)
        frames.append(base)
    strip = Image.new("RGBA", (s, s * 4))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * s))
    return strip


def make_progress(metal: Image.Image, teal_sample: Image.Image):
    bg = Image.new("RGB", (PB_W, PB_H), (24, 22, 20))
    tex = metal.resize((PB_W, PB_H), Image.Resampling.LANCZOS).convert("RGB")
    bg = Image.blend(bg, tex, 0.4)
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, PB_W - 1, PB_H - 1], outline=(110, 95, 55))
    d.rectangle([1, 1, PB_W - 2, PB_H - 2], outline=(18, 16, 14))

    fg = Image.new("RGB", (PB_W, PB_H), (8, 90, 100))
    t = teal_sample.convert("RGB").resize((PB_W, PB_H), Image.Resampling.LANCZOS)
    fg = Image.blend(fg, t, 0.7)
    fg = ImageEnhance.Color(fg).enhance(1.35)
    fg = ImageEnhance.Brightness(fg).enhance(1.2)
    d2 = ImageDraw.Draw(fg)
    d2.rectangle([0, 0, PB_W - 1, PB_H - 1], outline=(140, 240, 245))
    d2.line([(2, 2), (PB_W - 3, 2)], fill=(200, 255, 255))
    return bg, fg


def draw_rivet(d: ImageDraw.ImageDraw, cx: int, cy: int):
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(175, 145, 75), outline=(85, 65, 30))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(95, 75, 35))


def compose_background(
    header: Image.Image,
    metal: Image.Image,
    hero: Image.Image,
    floor: Image.Image,
    mode: str,
) -> Image.Image:
    canvas = Image.new("RGB", (UI_W, UI_H), (14, 12, 11))
    floor_img = ImageEnhance.Brightness(floor.resize((UI_W, UI_H), Image.Resampling.LANCZOS)).enhance(0.5)
    canvas.paste(floor_img, (0, 0))

    # darken mid for readability
    veil = Image.new("RGBA", (UI_W, UI_H), (0, 0, 0, 90))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), veil).convert("RGB")

    hdr = header.resize((UI_W, 70), Image.Resampling.LANCZOS)
    canvas.paste(hdr, (0, 0))

    # main chassis
    margin_x, top_y = 28, 78
    frame_w, frame_h = UI_W - margin_x * 2, UI_H - top_y - 18
    chassis = Image.new("RGB", (frame_w, frame_h), (42, 40, 36))
    metal_big = metal.resize((frame_w, frame_h), Image.Resampling.LANCZOS).convert("RGB")
    chassis = Image.blend(chassis, metal_big, 0.75)

    # upper illustration well
    well_pad = 18
    well_h = frame_h - 128
    well = Image.new("RGB", (frame_w - well_pad * 2, well_h), (18, 16, 14))
    # dark inset
    hero_max = (well.width - 12, well.height - 12)
    hero_img = ImageOps.contain(hero.convert("RGB"), hero_max)
    if mode == "installing":
        hero_img = ImageEnhance.Brightness(hero_img).enhance(0.42)
        hero_img = ImageEnhance.Color(hero_img).enhance(0.65)
        # dim overlay text hint area already baked; keep quiet
    hx = (well.width - hero_img.width) // 2
    hy = (well.height - hero_img.height) // 2
    well.paste(hero_img, (hx, hy))
    chassis.paste(well, (well_pad, 14))

    # lower control deck (dark brushed)
    deck = metal.resize((frame_w - 8, 108), Image.Resampling.LANCZOS).convert("RGB")
    deck = ImageEnhance.Brightness(deck).enhance(0.28)
    chassis.paste(deck, (4, frame_h - 112))

    # gold rim
    rim = Image.new("RGB", (frame_w + 10, frame_h + 10), (95, 78, 42))
    d = ImageDraw.Draw(rim)
    d.rectangle([0, 0, rim.width - 1, rim.height - 1], outline=(190, 160, 90))
    d.rectangle([1, 1, rim.width - 2, rim.height - 2], outline=(55, 45, 25))
    rim.paste(chassis, (5, 5))
    draw_rivet(d, 12, 12)
    draw_rivet(d, rim.width - 13, 12)
    draw_rivet(d, 12, rim.height - 13)
    draw_rivet(d, rim.width - 13, rim.height - 13)

    canvas.paste(rim, ((UI_W - rim.width) // 2, top_y))
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")

    header = im.crop(BOX_HEADER)
    left = im.crop(BOX_LEFT)
    right = im.crop(BOX_RIGHT)
    metal = im.crop(BOX_METAL)
    floor = im.crop(BOX_FLOOR)

    finish = im.crop(BOX_FINISH)
    install = im.crop(BOX_INSTALL)
    finish_dark = im.crop(BOX_FINISH_DARK)
    install_dark = im.crop(BOX_INSTALL_DARK)

    finish_btn = finish.resize((BTN_FINISH_W, BTN_H), Image.Resampling.LANCZOS)
    install_btn = install.resize((BTN_INSTALL_W, BTN_H), Image.Resampling.LANCZOS)
    finish_d = finish_dark.resize((BTN_FINISH_W, BTN_H), Image.Resampling.LANCZOS)
    install_d = install_dark.resize((BTN_INSTALL_W, BTN_H), Image.Resampling.LANCZOS)

    make_states(install_btn, install_d).save(OUT / "button_setup_or_next.png")
    make_states(finish_btn, finish_d).save(OUT / "button_finish.png")
    make_close_strip(metal).save(OUT / "button_close.png")

    pb_bg, pb_fg = make_progress(metal, install)
    pb_bg.save(OUT / "progressbar_background.png")
    pb_fg.save(OUT / "progressbar_foreground.png")

    compose_background(header, metal, right, floor, "welcome").save(OUT / "background_welcome.png")
    compose_background(header, metal, right, floor, "installing").save(OUT / "background_installing.png")
    compose_background(header, metal, left, floor, "finish").save(OUT / "background_finish.png")

    # debug
    finish.save(OUT / "_btn_finish_raw.png")
    install.save(OUT / "_btn_install_raw.png")
    finish_dark.save(OUT / "_btn_finish_dark_raw.png")
    install_dark.save(OUT / "_btn_install_dark_raw.png")
    left.save(OUT / "_panel_left.png")
    right.save(OUT / "_panel_right.png")

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
        p = OUT / name
        with Image.open(p) as img:
            print(f"{name}: {img.size}")


if __name__ == "__main__":
    main()
