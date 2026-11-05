# 5.27 step chains in the openings (analog 4.22: 50 | steps | 50 at the free end), dim line where the opening diagonal is high,
# short «50» texts inside the storey beside the line (not over the slab / diagonal / axis A)
import sys,json; sys.path.insert(0,'wl'); from common import *
from rowsplit import rows as ROWS
X,Y=2078100.0,455939.0; AX1=15030.0
L=[27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320]; SLAB=250.0
HD=json.load(open('wl/sm7_hor.json',encoding='utf-8'))['HD']
R=listwin(X,Y,42000,59400,None)
er=[r['h'] for r in R if r['t']=='DIMENSION' and len(r['sp'])>=3 and abs(r['sp'][0][0]-r['sp'][1][0])<1 and any(abs(r['sp'][0][0]-v)<2 for v in (AX1+3175,AX1+17100))]
ops=[dict(t='erase',h=er)]
W=lambda x,y:[X+AX1+x,Y+y]
for s in range(1,7):
    d,st=HD[s]; pos,segs=ROWS(L[s],L[s+1],st,SLAB); y0,y1=pos[0],pos[-1]
    for xf,dx in ((3175,1675),(17100,2200)):
        ch=[(L[s],y0,'')]+[(a,b,('%dх%d'%(v,k)) if k>1 else '') for a,b,v,k in segs]+[(y1,L[s+1]-SLAB,'')]
        for a,b,txt in ch:
            kw=dict(t='dim',h='WT_DV',p1=W(xf,a),p2=W(xf,b),dl=W(xf+dx,(a+b)/2),rot=1.5707963267948966,txt=txt)
            if b-a<450: kw['tx']=W(xf+dx-150,(a+520) if a==L[s] else (b-650))
            ops.append(kw)
ops.append(dict(t='save'))
print(len(er),len(ops)); out=gx.run(ops,'och'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l])
