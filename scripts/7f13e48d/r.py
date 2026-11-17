import fitz,sys
from PIL import Image
import numpy as np
O=r"D:\РАБОЧКА\ТUNAY STROY\Проект\Лестница\КМ Чертеж БЦ.pdf"
V1=r"D:\_claude_work\bc_lestnitsa\var\v1.pdf"
V2=r"D:\_claude_work\bc_lestnitsa\var\v2.pdf"
out=r"D:\_claude_work\bc_lestnitsa\var\chk"
d={k:fitz.open(p) for k,p in (('o',O),('v1',V1),('v2',V2))}
for k,doc in d.items(): print(k,len(doc),[ (round(p.rect.width),round(p.rect.height),p.rotation) for p in doc][:3])
def rend(doc,i,dpi=190):
    pm=doc[i].get_pixmap(dpi=dpi); return Image.frombytes("RGB",(pm.width,pm.height),pm.samples)
def quarters(k,i):
    im=rend(d[k],i); w,h=im.size
    for r in range(2):
        for c in range(2):
            im.crop((c*w//2,r*h//2,(c+1)*w//2,(r+1)*h//2)).save(f"{out}\{k}_p{i+1}_q{r*2+c+1}.png")
    print(k,i+1,im.size)
for i in [3,4,5,8,9,10]: quarters('v1',i)
for i in [2,3,4,5,8,9]: quarters('v2',i)
for i in [2,3,4,5,7,8,9,10]: quarters('o',i)
for i in [0,1,2,6,7,11,12,13]:
    a=np.array(rend(d['o'],i,100)).astype(int);b=np.array(rend(d['v1'],i,100)).astype(int)
    print('diff v1 p',i+1,a.shape==b.shape,(np.abs(a-b).sum(2)>30).sum() if a.shape==b.shape else 'shape')
