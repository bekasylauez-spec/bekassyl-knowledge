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
