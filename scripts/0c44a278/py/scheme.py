import ezdxf,json
from ezdxf import bbox
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
d=ezdxf.readfile(S+r'\b1.dxf'); m=d.modelspace()
out={}
for name,ins,fx0,fx1 in (('7.0',251800,388117,470217),('4.5',167700,304017,386117)):
    ox=141817.3+ins; oy=-1773284.1
    R={'dash':[],'solid':[],'col':[],'hatch':[]}
    for e in m:
        try: b=bbox.extents([e],fast=True)
        except: continue
        if not b.has_data or not(b.extmin.x>fx0 and b.extmax.x<fx1 and b.extmin.y>-1788184): continue
        if e.dxftype()=='LWPOLYLINE':
            pts=[(round(p[0]-ox,1),round(p[1]-oy,1)) for p in e.get_points()]
            if e.dxf.layer=='Размеры':
                R['dash' if e.dxf.get('linetype','')=='невидимая' else 'solid'].append([pts,e.closed])
            elif e.dxf.layer=='柱': R['col'].append([pts,e.closed])
        elif e.dxftype()=='HATCH':
            for p in e.paths:
                try: R['hatch'].append([(round(v[0]-ox,1),round(v[1]-oy,1)) for v in p.vertices])
                except: pass
    out[name]=R; print(name,{k:len(v) for k,v in R.items()})
json.dump(out,open(S+r'\scheme.json','w'))
