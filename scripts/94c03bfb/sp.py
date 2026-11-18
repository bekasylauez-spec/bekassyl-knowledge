import fitz,sys
from PIL import Image
out=sys.argv[1]
spec=[(1,(60,780,160,860)),(1,(1430,850,1560,910)),(1,(1790,740,1850,930)),(1,(40,740,110,930)),(1,(690,200,770,260)),(4,(1720,930,1850,990)),(4,(100,780,180,850)),(2,(1440,850,1560,910)),(3,(1440,850,1560,910)),(3,(2000,60,2150,120))]
ims=[]
for n,r in spec:
    pg=fitz.open(r'D:\_claude_work\Kasymova\revit\_check\v10\s2.%d.pdf'%n)[0]
    p=pg.get_pixmap(dpi=250,clip=fitz.Rect(*r)); p.save(out+r'\q\t.png'); im=Image.open(out+r'\q\t.png').copy(); im.thumbnail((560,560)); ims.append(im)
M=Image.new('RGB',(560*4,560*3),'white')
for i,im in enumerate(ims): M.paste(im,((i%4)*560,(i//4)*560))
M.save(out+r'\q\spot.png')
