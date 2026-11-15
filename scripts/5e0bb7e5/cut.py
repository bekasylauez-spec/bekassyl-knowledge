import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import glob
d=r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру"
for n,f in (("a","Парақ_КЖ-3-2_Ростверк Рс-1 подколонник Пк-1 Армирование.png"),("b","Парақ_КЖ-3-3_Ростверк Рс-2 подколонник Пк-2 Армирование.png")):
    im=Image.open(d+"\\"+f); print(n,im.size)
    W,H=im.size
    im.resize((W//3,H//3)).save(sys.argv[1]+f"\\{n}_full.png")
    for i in range(2):
        for j in range(2):
            c=im.crop((j*W//2,i*H//2,(j+1)*W//2,(i+1)*H//2)); c=c.resize((c.width*190//256,c.height*190//256)); c.save(sys.argv[1]+f"\\{n}_q{i}{j}.png")
