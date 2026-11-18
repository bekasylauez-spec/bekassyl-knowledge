import fitz,sys
from ov import words
def segs(p):
    S=[]
    for d in p.get_drawings():
        w=d.get("width") or 0
        for it in d["items"]:
            if it[0]=="l":
                S.append((it[1],it[2],w,d))
            elif it[0]=="re":
                r=it[1]
                for a,b in ((r.tl,r.tr),(r.tr,r.br),(r.br,r.bl),(r.bl,r.tl)):
                    S.append((a,b,w,d))
            elif it[0]=="qu":
                q=it[1]
                pts=[q.ul,q.ur,q.lr,q.ll]
                for k in range(4): S.append((pts[k],pts[(k+1)%4],w,d))
    return S
def inter(a,b,r):
    # liang-barsky seg vs rect
    x0,y0,x1,y1=a.x,a.y,b.x,b.y
    dx,dy=x1-x0,y1-y0
    t0,t1=0,1
    for p_,q_ in ((-dx,x0-r.x0),(dx,r.x1-x0),(-dy,y0-r.y0),(dy,r.y1-y0)):
        if p_==0:
            if q_<0: return False
        else:
            t=q_/p_
            if p_<0:
                if t>t1:return False
                t0=max(t0,t)
            else:
                if t<t0:return False
                t1=min(t1,t)
    return t0<=t1
if __name__=="__main__":
    n=int(sys.argv[1])
    p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
    W=words(p);S=segs(p)
    print(len(S))
    for t,r,sz,v in W:
        rr=fitz.Rect(r.x0+0.3,r.y0+0.3,r.x1-0.3,r.y1-0.3) if not v else fitz.Rect(r.x0+0.3,r.y0+0.3,r.x1-0.3,r.y1-0.3)
        hits=[(s[2]) for s in S if inter(s[0],s[1],rr)]
        if hits: print(t,[round(v) for v in (r.x0,r.y0,r.x1,r.y1)],len(hits),sorted(set(round(h,2) for h in hits)))
