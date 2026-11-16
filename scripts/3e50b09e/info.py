import sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
for f in sorted(glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-*.png")):
    im = Image.open(f)
    print(os.path.basename(f), im.size, im.mode, round(im.size[0]/im.size[1],4), os.path.getsize(f)//1024, "KB")
for f in ["M_10","M_15","M_20","X2","M_07","M_04"]:
    p = r"D:\РАБОЧКА\КЖ_Инструменты\шаблон_парақтары\%s.png" % f
    if os.path.exists(p):
        im = Image.open(p); print(f, im.size)
