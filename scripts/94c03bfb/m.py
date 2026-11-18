import fitz,sys
from PIL import Image
specs=[(2,1500,730,1660,800),(4,1640,1440,1740,1500),(3,1960,430,2130,620),(4,860,560,960,640),(1,1040,630,1150,700),(5,1800,740,1990,830)]
ims=[]
for i,x0,y0,x1,y1 in specs:
    p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{i}.pdf")[0]
    pm=p.get_pixmap(dpi=300,clip=fitz.Rect(x0,y0,x1,y1))
    ims.append(Image.frombytes("RGB",(pm.width,pm.height),pm.samples))
W=max(i.width for i in ims);H=sum(i.height for i in ims)+10*len(ims)
c=Image.new("RGB",(W,H),"white");y=0
for im in ims: c.paste(im,(0,y)); y+=im.height+10
c.save("q/m.png");print(c.size)
