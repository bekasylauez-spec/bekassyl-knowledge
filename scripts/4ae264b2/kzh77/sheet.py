from PIL import Image, ImageDraw
import sys
S=r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\4ae264b2-3d49-4a11-8864-2d6523e82a02\scratchpad\png"
pages=[int(x) for x in sys.argv[2:]]
W=480;cols=4
ims=[]
for p in pages:
    im=Image.open(S+r"\p%03d.png"%p); im.thumbnail((W,W)); ims.append((p,im))
rows=(len(ims)+cols-1)//cols
out=Image.new('RGB',(cols*(W+10),rows*(W*0.75+30).__int__()),'white')
d=ImageDraw.Draw(out)
for i,(p,im) in enumerate(ims):
    x=(i%cols)*(W+10); y=(i//cols)*int(W*0.75+30)
    out.paste(im,(x,y+20)); d.text((x+5,y+2),str(p),fill='red')
out.save(S+"\\"+sys.argv[1])
