import sys
from PIL import Image
d=sys.argv[1]; out=sys.argv[2]; names=sys.argv[3:]
ims=[Image.open(d+'\\'+n+' - 3D вид - КМ проверка.png').convert('RGB') for n in names]
ims=[im.resize((800,int(800*im.size[1]/im.size[0]))) for im in ims]
W=800*3; H=max(i.size[1] for i in ims)*2
can=Image.new('RGB',(W,H),'white')
for k,im in enumerate(ims): can.paste(im,((k%3)*800,(k//3)*(H//2)))
can.save(out)