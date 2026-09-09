# -*- coding: utf-8 -*-
"""Precise probe of new UI mockup with tight boxes."""
import os
from PIL import Image, ImageDraw

SRC = r"D:\code_yingie\插件打包工具\tmp\_src_ui.png"
OUT = r"D:\code_yingie\插件打包工具\tmp\probe"
os.makedirs(OUT, exist_ok=True)

im = Image.open(SRC).convert("RGB")
print("size", im.size)

# Tuned boxes for 1024x479 sheet
boxes = {
    "00_full": (0, 0, 1024, 479),
    "01_header_title": (280, 10, 740, 72),
    "02_chassis": (55, 68, 970, 318),
    "03_left_done": (85, 105, 490, 245),
    "04_right_vst": (505, 100, 945, 255),
    "05_btn_finish": (95, 345, 228, 395),
    "06_btn_install": (255, 345, 478, 395),
    "07_btn_finish_dark": (95, 400, 228, 452),
    "08_btn_install_dark": (255, 400, 478, 452),
    "09_gold_label1": (520, 350, 880, 395),
    "10_gold_label2": (520, 405, 880, 450),
    "11_lower_metal": (70, 250, 960, 315),
    "12_floor": (0, 310, 1024, 479),
}

ann = im.copy()
d = ImageDraw.Draw(ann)
for name, box in boxes.items():
    if name == "00_full":
        continue
    d.rectangle([box[0], box[1], box[2]-1, box[3]-1], outline=(0, 255, 0), width=2)
    d.text((box[0]+3, box[1]+3), name, fill=(0, 255, 0))
    c = im.crop(box)
    c.save(os.path.join(OUT, f"{name}.png"))
    print(name, c.size)

ann.save(os.path.join(OUT, "_annotated.png"))
print("annotated saved")
