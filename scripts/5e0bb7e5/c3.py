from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import glob
f=[x for x in glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\*.png") if "КЖ-3-2" in x][0]
im=Image.open(f).convert("RGB")
im.crop((1780,330,3250,1560)).save(r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e0bb7e5-4cf8-45cd-890e-18c55e1758cc\scratchpad\s11.png")
