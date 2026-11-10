import ezdxf,sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
L=[e for e in msp if e.dxftype()=='INSERT' and e.dxf.name=='купук']
# stamps xr
S=sorted([(round((e.dxf.insert.x+248096)/100)*100, round((e.dxf.insert.y-338877.2)/100)*100) for e in L],key=lambda s:(s[1],s[0]))
import collections
# per row prev stamp
rows=collections.defaultdict(list)
for x,y in S: rows[y].append(x)
pts=[]
for e in msp:
    if e.dxftype() in('LINE','LWPOLYLINE','CIRCLE','ARC','TEXT','MTEXT','DIMENSION','INSERT','HATCH','POLYLINE'):
        try: b=bbox.extents([e])
        except: continue
        if b.has_data: pts.append((b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y,e.dxf.layer))
for y,xs in rows.items():
    xs.sort()
    print('row',y,xs)
    for i,x in enumerate(xs):
        left = xs[i-1] if i else x-100000
        X0=max(left+1000,x-100000);X1=x+600
        sel=[p for p in pts if p[0]>=X0 and p[2]<=X1 and p[1]>=y-3000 and p[3]<=y+60000 and p[4] not in('1Штамп',)]
        if not sel: print(x,'-');continue
        print(x,'content bbox',round(min(p[0] for p in sel)),round(min(p[1] for p in sel)),round(max(p[2] for p in sel)),round(max(p[3] for p in sel)),len(sel))
