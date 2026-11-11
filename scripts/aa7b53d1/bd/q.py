import ezdxf
doc=ezdxf.readfile('w.dxf'); msp=doc.modelspace()
e=doc.entitydb['14E3E6']; print('style',e.dxf.style, doc.styles.get(e.dxf.style).dxf.font, doc.styles.get(e.dxf.style).dxf.get('bigfont'))
e=doc.entitydb['1285A9']; print('style OD',e.dxf.style, doc.styles.get(e.dxf.style).dxf.font)
for d in msp.query('DIMENSION'):
    try: m=d.get_measurement()
    except: continue
    if abs(m-160000)<1 or abs(m-150500)<1: print('DIM',d.dxf.handle,m,d.dxf.defpoint, d.dxf.get('text_midpoint'))
for m in msp.query('MTEXT'):
    t=m.text
    if 'идрошпонк' in t and 'Наружную' in t or 'Монтаж гидрошпонок' in t:
        print('NOTE3',m.dxf.handle,m.dxf.insert,m.dxf.char_height,m.dxf.width,m.dxf.style); print(repr(t))
# lines near trap table
x0,y0=2776087,1034761
n=0
for l in msp.query('LINE LWPOLYLINE INSERT'):
    try: p=l.dxf.start if l.dxftype()=='LINE' else (l.dxf.insert if l.dxftype()=='INSERT' else l.get_points()[0])
    except: continue
    if x0-200<p[0]<x0+4600 and y0-1300<p[1]<y0+100: n+=1; print('NEAR',l.dxftype(),l.dxf.handle,p[:2])
print(n)
