import ezdxf, sys, pickle
doc = ezdxf.readfile('live1.dxf')
msp = doc.modelspace()
for e in msp:
    t = e.dxftype()
    s = None
    if t in ('TEXT','MTEXT'):
        s = e.dxf.text if t=='TEXT' else e.text
    if s and ('Рб' in s or 'андбал' in s):
        print(t, e.dxf.handle, s[:60], tuple(round(v) for v in e.dxf.insert)[:2])
