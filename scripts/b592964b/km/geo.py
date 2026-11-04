# geo.py <dxf> x0,y0,x1,y1 [types]  -> entity geometry (abs coords) whose bbox centre in window
import ezdxf, sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
ty_f = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None
r = lambda v: round(v, 1)
for e in msp:
    ty = e.dxftype()
    if ty_f and ty not in ty_f: continue
    try: b = bbox.extents([e])
    except Exception: continue
    if not b.has_data: continue
    cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
    if not (x0 <= cx <= x1 and y0 <= cy <= y1): continue
    try: lay = e.dxf.layer
    except Exception: lay = '?'
    g = ''
    if ty == 'LINE': g = f'{r(e.dxf.start.x)},{r(e.dxf.start.y)} -> {r(e.dxf.end.x)},{r(e.dxf.end.y)}'
    elif ty == 'LWPOLYLINE': g = ' '.join(f'{r(p[0])},{r(p[1])}' + (f'b{round(p[4],3)}' if p[4] else '') for p in e.get_points()) + (' C' if e.closed else '')
    elif ty == 'INSERT': g = f'{e.dxf.name} @{r(e.dxf.insert.x)},{r(e.dxf.insert.y)} s{r(e.dxf.xscale)},{r(e.dxf.yscale)} rot{r(e.dxf.rotation)}'
    elif ty == 'DIMENSION': g = f'm{r(e.get_measurement())} p1 {r(e.dxf.defpoint2.x)},{r(e.dxf.defpoint2.y)} p2 {r(e.dxf.defpoint3.x)},{r(e.dxf.defpoint3.y)} dl {r(e.dxf.defpoint.x)},{r(e.dxf.defpoint.y)} txt[{e.dxf.text}]'
    elif ty in ('TEXT',): g = f'"{e.dxf.text}" @{r(e.dxf.insert.x)},{r(e.dxf.insert.y)} h{r(e.dxf.height)}'
    elif ty == 'MTEXT': g = f'"{e.plain_text()[:60]}" @{r(e.dxf.insert.x)},{r(e.dxf.insert.y)}'
    elif ty == 'CIRCLE': g = f'c{r(e.dxf.center.x)},{r(e.dxf.center.y)} r{r(e.dxf.radius)}'
    elif ty == 'ARC': g = f'c{r(e.dxf.center.x)},{r(e.dxf.center.y)} r{r(e.dxf.radius)} {r(e.dxf.start_angle)}-{r(e.dxf.end_angle)}'
    else: g = f'bbox {r(b.extmin.x)},{r(b.extmin.y)} {r(b.extmax.x)},{r(b.extmax.y)}'
    print(ty, e.dxf.handle, lay, g)
