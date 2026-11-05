import ezdxf,ezdxf.bbox as BB,json,sys,pickle
F=json.load(open('frames.json'))[sys.argv[1]][int(sys.argv[2])]; x0,y0=F[0],F[1]
win=list(map(float,sys.argv[3:7]))
d=ezdxf.readfile(sys.argv[1]+'.dxf'); m=d.modelspace()
rows=[]
for e in m:
    try: b=BB.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    X=b.extmin.x-x0; Y=b.extmin.y-y0
    if X<win[0] or b.extmax.x-x0>win[2] or Y<win[1] or b.extmax.y-y0>win[3]: continue
    t=e.dxftype(); s=''
    if t=='LINE': s='%.0f,%.0f-%.0f,%.0f'%(e.dxf.start.x-x0,e.dxf.start.y-y0,e.dxf.end.x-x0,e.dxf.end.y-y0)
    elif t in('TEXT','MTEXT'): s=(e.dxf.text if t=='TEXT' else e.text)[:30]+' h=%.0f'%(e.dxf.height if t=='TEXT' else e.dxf.char_height)
    elif t=='DIMENSION':
        o=e.override(); s='%s st=%s lfac=%s'%(e.dxf.get('text',''),e.dxf.dimstyle,o.get('dimlfac',1))
    elif t=='LWPOLYLINE': s='n=%d cw=%s pts=%s'%(len(e),e.dxf.get('const_width',0),[(round(p[0]-x0),round(p[1]-y0)) for p in e.get_points()][:6])
    elif t=='CIRCLE': s='r=%.1f'%e.dxf.radius
    elif t=='INSERT': s=e.dxf.name
    rows.append((t,e.dxf.layer,round(X),round(Y),round(b.size.x),round(b.size.y),e.dxf.handle,s,e.dxf.get('lineweight',-9),e.dxf.get('color',256)))
rows.sort(key=lambda r:(r[0],r[1],-r[3]))
for r in rows: print(r)
