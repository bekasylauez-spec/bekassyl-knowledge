import fitz,sys
sys.path.insert(0,'.')
from grid import grid,loc
def wedges(p):
    out=[]
    for d in p.get_drawings():
        w=d.get("width") or 0
        if w<0.9: continue
        for it in d["items"]:
            if it[0]!="l":continue
            a,b=it[1],it[2]
            dx,dy=b.x-a.x,b.y-a.y
            L=(dx*dx+dy*dy)**.5
            if L<4:continue
            if (abs(dx)>3 and 0.03<abs(dy/dx)<0.3) or (abs(dy)>3 and 0.03<abs(dx/dy)<0.3):
                out.append((a.x,a.y,b.x,b.y,L,w))
    return out
if __name__=="__main__":
    for n in range(1,9):
        p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
        g=grid(p)
        ws=wedges(p)
        print("PAGE",n,len(ws))
        for w in ws: print("  ",[round(v,1) for v in w], loc(p,(w[0]+w[2])/2,(w[1]+w[3])/2,g))
