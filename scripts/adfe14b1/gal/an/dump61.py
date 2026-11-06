import ezdxf,sys
d=ezdxf.readfile('a61.dxf'); m=d.modelspace()
X0,Y0,X1,Y1=[float(v) for v in sys.argv[1:5]]
def inside(x,y): return X0<=x<=X1 and Y0<=y<=Y1
rows=[]
for e in m:
    t=e.dxftype(); h=e.dxf.handle; L=e.dxf.layer
    try:
        if t=='LINE':
            a,b=e.dxf.start,e.dxf.end
            if inside(a.x,a.y): rows.append((t,h,L,'%.0f,%.0f -> %.0f,%.0f'%(a.x,a.y,b.x,b.y)))
        elif t=='LWPOLYLINE':
            p=list(e.get_points('xy'))
            if inside(*p[0]): rows.append((t,h,L,' '.join('%.0f,%.0f'%q for q in p[:8])+(' closed' if e.closed else '')+' w%.0f'%e.dxf.const_width if e.dxf.hasattr('const_width') else ''))
        elif t in('TEXT','MTEXT'):
            p=e.dxf.insert
            if inside(p.x,p.y): rows.append((t,h,L,'%.0f,%.0f h%.0f %r'%(p.x,p.y,e.dxf.char_height if t=='MTEXT' else e.dxf.height,(e.plain_text() if t=='MTEXT' else e.dxf.text)[:70])))
        elif t=='DIMENSION':
            p=e.dxf.defpoint
            a=e.dxf.defpoint2; b=e.dxf.defpoint3
            if inside(a.x,a.y) or inside(p.x,p.y): rows.append((t,h,L,'p1 %.0f,%.0f p2 %.0f,%.0f dl %.0f,%.0f txt=%r meas=%.0f st=%s'%(a.x,a.y,b.x,b.y,p.x,p.y,e.dxf.text,e.get_measurement() if hasattr(e,'get_measurement') else -1,e.dxf.dimstyle)))
        elif t in ('INSERT',):
            p=e.dxf.insert
            if inside(p.x,p.y): rows.append((t,h,L,'%.0f,%.0f blk=%s sc=%.2f rot=%.0f'%(p.x,p.y,e.dxf.name,e.dxf.xscale,e.dxf.rotation)))
        elif t=='CIRCLE':
            p=e.dxf.center
            if inside(p.x,p.y): rows.append((t,h,L,'%.0f,%.0f r%.0f'%(p.x,p.y,e.dxf.radius)))
        elif t=='HATCH':
            rows.append((t,h,L,'hatch'))
    except Exception as ex: pass
for r in rows: print('\t'.join(r))
