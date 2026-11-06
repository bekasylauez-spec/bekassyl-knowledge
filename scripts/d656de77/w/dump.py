import ezdxf, sys, collections
from ezdxf import bbox
doc=ezdxf.readfile(r'w\gxr.dxf'); msp=doc.modelspace()
k=int(sys.argv[1]); X0=172179+31500*k; Y0=455939
win=(X0-200,Y0-200,X0+31700,Y0+15100)
def pt(e):
    try:
        if e.dxftype() in('TEXT','MTEXT','INSERT','CIRCLE'): p=e.dxf.insert if e.dxftype()!='CIRCLE' else e.dxf.center; return p[0],p[1]
        if e.dxftype()=='LINE': return e.dxf.start[0],e.dxf.start[1]
        if e.dxftype()=='LWPOLYLINE': p=e.get_points()[0]; return p[0],p[1]
        if e.dxftype()=='DIMENSION': p=e.dxf.defpoint; return p[0],p[1]
    except Exception: return None
    return None
cnt=collections.Counter()
for e in msp:
    p=pt(e)
    if p is None:
        continue
    if p is None or not(win[0]<=p[0]<=win[2] and win[1]<=p[1]<=win[3]): continue
    t=e.dxftype(); cnt[(t,e.dxf.get('layer','?'))]+=1
    s=''
    if t=='TEXT': s=e.dxf.text
    elif t=='MTEXT': s=e.plain_text()[:60]
    elif t=='INSERT': s='blk '+e.dxf.name
    elif t=='DIMENSION': s='dim '+str(e.dxf.get('text',''))+' m=%.0f'%e.get_measurement() if hasattr(e,'get_measurement') else ''
    elif t=='LWPOLYLINE': s='pl n=%d %s'%(len(e),[tuple(round(v) for v in q[:2]) for q in e.get_points()][:4])
    elif t=='LINE': s='ln %s-%s'%(tuple(round(v) for v in e.dxf.start[:2]),tuple(round(v) for v in e.dxf.end[:2]))
    elif t=='CIRCLE': s='c r=%.0f'%e.dxf.radius
    if len(sys.argv)>2: print(t,e.dxf.handle,e.dxf.get('layer','?'),'%.0f,%.0f'%(p[0]-X0,p[1]-Y0),s)
for k2,v in sorted(cnt.items()): print(k2,v)
