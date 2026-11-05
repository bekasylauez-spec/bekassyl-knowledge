import ezdxf
doc = ezdxf.readfile(r'w/kt.dxf'); msp = doc.modelspace(); seen = set()
for e in msp.query('TEXT MTEXT'):
    s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
    if ('армирование монолитной' in s or 'Опалубочный' in s) and 'См-' in s:
        t = s.replace('{\L', '').replace('}', '')
        if t not in seen: seen.add(t); print(round(e.dxf.insert.x), t[:150])
