import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру"
b=Image.open(d+r"\Парақ_КЖ-3-3_Ростверк Рс-2 подколонник Пк-2 Армирование.png")
b.crop((700,650,1450,1350)).save(sys.argv[1]+r"\b_plan.png")
b.crop((2150,350,3300,1250)).save(sys.argv[1]+r"\b_s11.png")
