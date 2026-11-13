import ezdxf,collections
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf'); msp=doc.modelspace()
X0,X1,Y0,Y1=1050000,1109400,95516,137516
c=collections.defaultdict(list); n=0
for e in msp:
    t=e.dxftype()
    try:
        if t=='LINE': pts=tuple(sorted([tuple(round(v) for v in e.dxf.start)[:2],tuple(round(v) for v in e.dxf.end)[:2]]))
        elif t=='LWPOLYLINE': pts=tuple(sorted(tuple(round(float(v)) for v in p[:2]) for p in e.get_points()))
        else: continue
    except: continue
    if not any(X0<=p[0]<=X1 and Y0<=p[1]<=Y1 for p in pts): continue
    n+=1; c[(t,pts)].append(e.dxf.handle)
print(n)
for k,v in c.items():
    if len(v)>1: print(len(v),k[0],k[1][:4],v)
