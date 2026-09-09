# -*- coding: utf-8 -*-
from PIL import Image

src = r'C:\Users\Administrator\.cursor\projects\d-code-yingie\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_1788938253179_d-84c3cb79-c55d-4c2a-b0bc-480b514ac33e.png'
out = r'D:\code_yingie\插件打包工具\tmp'
im = Image.open(src).convert('RGB')

# Candidate crops for inspection
crops = {
    'hdr': (0, 0, 1024, 90),
    'frame': (40, 70, 980, 340),
    'left_panel': (70, 95, 500, 250),
    'right_panel': (500, 95, 960, 250),
    'btns_area': (60, 320, 500, 420),
    'gold_btns': (520, 340, 900, 440),
    'finish_btn': (80, 340, 230, 400),
    'install_btn': (240, 340, 480, 400),
    'install_btn_dark': (240, 395, 480, 455),
}
for name, box in crops.items():
    im.crop(box).save(f'{out}\\_crop_{name}.png')
    print(name, box, im.crop(box).size)
