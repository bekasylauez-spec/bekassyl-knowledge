import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
D="D:/_claude_work/zavod_km_uz/plates/"
X0={25:2894065,28:2915065,38:3681900}
def crop(sh,x0,y0,x1,y1,out,scale=3):
    im=Image.open(D+'s%d.png'%sh)
    W,H=im.size
    def px(x,y): return ((x-(X0[sh]-50))/4300*W, (-271630-y)/3070*H)
    a=px(x0,y1);b=px(x1,y0)
    c=im.crop((int(a[0]),int(a[1]),int(b[0]),int(b[1])))
    c=c.resize((c.width*scale,c.height*scale),Image.LANCZOS)
    c.save(out)
sh=int(sys.argv[1]);v=list(map(float,sys.argv[2:6]));crop(sh,*v,sys.argv[6],int(sys.argv[7]) if len(sys.argv)>7 else 3)
