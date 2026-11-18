import fitz,sys
sys.path.insert(0,'.')
from ov import words
from ov2 import segs,inter
from grid import grid,loc
def run(n,verbose=True):
    p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
    g=grid(p)
    W=words(p);S=segs(p)
    res=[]
    for t,r,sz,v in W:
        if len(t.strip())<2 and not t.strip().isdigit(): continue
        # interior band: shrink 18% each side along both; core band thin axis middle 40%
        dx=r.width*0.12; dy=r.height*0.12
        rr=fitz.Rect(r.x0+dx,r.y0+dy,r.x1-dx,r.y1-dy)
        # for hatched text (marks inside walls) ignore width<0.3 hatch
        hits=[]
        for a,b,w,d in S:
            if w<0.1: continue
            if inter(a,b,rr):
                if (abs(a.x-b.x)+abs(a.y-b.y))<0.6: continue
                hits.append((round(a.x),round(a.y),round(b.x),round(b.y),round(w,2)))
        if hits: res.append((t,r,hits))
    return p,g,res
if __name__=="__main__":
    n=int(sys.argv[1])
    p,g,res=run(n)
    for t,r,h in res:
        print(repr(t) if t.isascii() else len(t),[round(v) for v in (r.x0,r.y0,r.x1,r.y1)],loc(p,(r.x0+r.x1)/2,(r.y0+r.y1)/2,g),len(h),h[:3])
