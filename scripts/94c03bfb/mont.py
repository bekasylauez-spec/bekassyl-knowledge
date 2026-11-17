import fitz,sys
from PIL import Image
d=fitz.open('sec5.pdf')
pages=[int(x) for x in sys.argv[1].split(',')]
rect=[float(x) for x in sys.argv[2].split(',')]
dpi=int(sys.argv[3]); out=sys.argv[4]
ims=[]
for n in pages:
    p=d[n-1]
    pix=p.get_pixmap(dpi=dpi,clip=fitz.Rect(*rect))
    pix.save('dc5/_t.png'); ims.append(Image.open('dc5/_t.png').copy())
w=max(i.width for i in ims);h=sum(i.height for i in ims)
m=Image.new('RGB',(w,h),'white');y=0
for i in ims: m.paste(i,(0,y));y+=i.height
m.save(out)
