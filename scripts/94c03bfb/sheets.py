import fitz,sys
sys.path.insert(0,'.')
from wedge import wedges
from grid import grid,loc
from PIL import Image,ImageDraw
def clusters(ws,r=70):
    cs=[]
    for w in ws:
        cx,cy=(w[0]+w[2])/2,(w[1]+w[3])/2
        for c in cs:
            if abs(c[0]-cx)<r and abs(c[1]-cy)<r:
                c[2].append(w);break
        else: cs.append([cx,cy,[w]])
    return cs
n=int(sys.argv[1])
p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
g=grid(p)
cs=clusters(wedges(p))
tiles=[]
for i,(cx,cy,ws) in enumerate(cs):
    xs=[v for w in ws for v in (w[0],w[2])];ys=[v for w in ws for v in (w[1],w[3])]
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    R=fitz.Rect(cx-95,cy-80,cx+95,cy+80)
    pm=p.get_pixmap(dpi=280,clip=R)
    im=Image.frombytes("RGB",(pm.width,pm.height),pm.samples)
    ImageDraw.Draw(im).text((5,5),f"#{i} ({cx:.0f},{cy:.0f}) {loc(p,cx,cy,g)}",fill=(255,0,0))
    tiles.append(im)
    print(i,round(cx),round(cy),loc(p,cx,cy,g),len(ws))
W,H=tiles[0].size
per=6
for s in range(0,len(tiles),per):
    sub=tiles[s:s+per]
    sh=Image.new("RGB",(W*2,H*3),"white")
    for k,t in enumerate(sub):
        sh.paste(t,((k%2)*W,(k//2)*H))
    sh.save(f"sh{n}_{s//per}.png")
