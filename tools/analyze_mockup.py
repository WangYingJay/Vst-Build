# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

src = r'C:\Users\Administrator\.cursor\projects\d-code-yingie\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_1788938253179_d-84c3cb79-c55d-4c2a-b0bc-480b514ac33e.png'
out_dir = r'D:\code_yingie\插件打包工具\tmp'
im = Image.open(src).convert('RGB')
w, h = im.size
print('size', w, h)
px = im.load()


def row_brightness(y):
    s = 0
    for x in range(w):
        r, g, b = px[x, y]
        s += r + g + b
    return s / (3 * w)


teal = []
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        if g > 140 and b > 100 and r < 120 and (g - r) > 40:
            teal.append((x, y))
if teal:
    xs = [p[0] for p in teal]
    ys = [p[1] for p in teal]
    print('teal bbox', min(xs), min(ys), max(xs), max(ys), 'count', len(teal))

red = []
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        if r > 160 and g < 90 and b < 90 and (r - g) > 80:
            red.append((x, y))
if red:
    xs = [p[0] for p in red]
    ys = [p[1] for p in red]
    print('red bbox', min(xs), min(ys), max(xs), max(ys), 'count', len(red))

# gold/bronze frame pixels
gold = []
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        if r > 120 and g > 90 and b < 90 and abs(r - g) < 50:
            gold.append((x, y))
if gold:
    xs = [p[0] for p in gold]
    ys = [p[1] for p in gold]
    print('gold bbox', min(xs), min(ys), max(xs), max(ys), 'count', len(gold))

ov = im.copy()
d = ImageDraw.Draw(ov)
for x in range(0, w, 50):
    d.line([(x, 0), (x, h)], fill=(0, 255, 0), width=1)
    d.text((x + 2, 2), str(x), fill=(0, 255, 0))
for y in range(0, h, 25):
    d.line([(0, y), (w, y)], fill=(255, 0, 0), width=1)
    d.text((2, y + 1), str(y), fill=(255, 0, 0))
ov.save(out_dir + r'\_grid.png')
print('saved grid')

for y in range(0, h, 20):
    print(f'row {y}: {row_brightness(y):.1f}')
