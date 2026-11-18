import fitz,sys
sys.path.insert(0,'.')
from wedge import wedges
from sheets_cl import clusters
for n in range(1,9):
    p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
    ws=wedges(p)
    W=[(w[4:6],w) for w in ws]
    words=p.get_text("words")
    print("PAGE",n)
    for cx,cy,grp in clusters(ws):
        for w in grp:
            x0,y0,x1,y1,L,wd=w
            frag = wd>1.3
            sc=0.0567 if frag else 0.02835
            horiz=abs(x1-x0)>abs(y1-y0)
            mm=L/sc
            # tolerance: opening dims typical; find numeric words within 90pt of midpoint
            mx,my=(x0+x1)/2,(y0+y1)/2
            near=[]
            for a,b,c,d,t,*_ in words:
                if t.isdigit() and abs((a+c)/2-mx)<110 and abs((b+d)/2-my)<110:
                    near.append(int(t))
            ok=[v for v in near if abs(v-mm)<0.12*mm]
            print(f"  ({mx:.0f},{my:.0f}) {'H' if horiz else 'V'} L={mm:.0f}mm frag={frag} match={ok}")
