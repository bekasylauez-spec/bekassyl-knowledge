import re,math,collections
rows=[]
for l in open("w/s5geo.txt",encoding="utf-8"):
    p=l.split()
    pts=[tuple(map(float,t)) for t in re.findall(r"\((-?[\d.]+), (-?[\d.]+), (-?[\d.]+)\)",l)]
    L=float(p[-1]); rows.append((p[1],p[2],p[3],pts,L))
# classify
for h,lay,lt,pts,L in rows:
    a,b=pts[0],pts[-1]
    dx=b[0]-a[0];dy=b[1]-a[1]
    kind="V" if abs(dx)<1 else ("H" if abs(dy)<1 else "D")
    print(h,lay,lt,kind,len(pts),round(a[0]),round(a[1]),round(b[0]),round(b[1]),round(L))
