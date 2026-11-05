import fitz,sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
pdf,name,dpi=sys.argv[1],sys.argv[2],int(sys.argv[3])
boxes=[tuple(map(float,b.split(','))) for b in sys.argv[4:]]   # fractions x0,y0,x1,y1 of the visible page
d=fitz.open(pdf);p=d[0];pm=p.get_pixmap(dpi=dpi)
im=Image.frombytes('RGB',(pm.width,pm.height),pm.samples)
for i,(a,b,c,e) in enumerate(boxes):
    W,H=im.size; im.crop((int(a*W),int(b*H),int(c*W),int(e*H))).save('w/%s_%d.png'%(name,i))
print(im.size)
