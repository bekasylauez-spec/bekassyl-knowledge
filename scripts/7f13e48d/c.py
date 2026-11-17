import fitz,sys
from PIL import Image
V2=r"D:\_claude_work\bc_lestnitsa\var\v2.pdf";V1=r"D:\_claude_work\bc_lestnitsa\var\v1.pdf"
out=r"D:\_claude_work\bc_lestnitsa\var\chk"
def crop(f,pg,box,name,dpi=300):
    d=fitz.open(f);p=d[pg-1]
    pm=p.get_pixmap(dpi=dpi);im=Image.frombytes("RGB",(pm.width,pm.height),pm.samples)
    s=dpi/190
    b=tuple(int(x*s) for x in box)
    im.crop(b).save(f"{out}\{name}.png");print(name,im.size)
# p4 coords at 190dpi full page: q1 offset 0,0 ; q2 offset 1571,0 (w//2)
O=r"D:\РАБОЧКА\ТUNAY STROY\Проект\Лестница\КМ Чертеж БЦ.pdf"
crop(O,3,(1111,500,1900,1790),'z_o_p3_tbl_r',dpi=190)
