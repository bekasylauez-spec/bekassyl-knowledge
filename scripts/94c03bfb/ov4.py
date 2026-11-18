import fitz,sys,math
sys.path.insert(0,'.')
from ov import words
from ov2 import segs,inter
def run(n):
    p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
    W=words(p);S=segs(p)
    out=[]
    for t,r,sz,v in W:
        if t.startswith('18.') or not t.strip(): continue
        if r.y0>1640 or r.x0<20: continue
        dx=r.width*0.2; dy=r.height*0.15
        rr=fitz.Rect(r.x0+dx,r.y0+dy,r.x1-dx,r.y1-dy)
        if rr.is_empty: continue
        hits=[]
        for a,b,w,d in S:
            sx,sy=abs(b.x-a.x),abs(b.y-a.y)
            L=math.hypot(sx,sy)
            if L<2: continue
            vertl = sx<0.15*L; horl = sy<0.15*L
            if not v and not vertl: continue
            if v and not horl: continue
            if inter(a,b,rr): hits.append((round(a.x),round(a.y),round(b.x),round(b.y),round(w,2)))
        if hits: out.append((t,r,hits))
    return p,out
if __name__=="__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    for n in map(int,sys.argv[1:]):
        p,out=run(n)
        print("PAGE",n,len(out))
        for t,r,h in out: print("  ",t,[round(x) for x in (r.x0,r.y0,r.x1,r.y1)],h[:2])
