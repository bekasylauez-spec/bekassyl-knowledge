import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1])
msp=d.modelspace()
print(collections.Counter(e.dxftype() for e in msp))
for e in msp.query('ACAD_TABLE'):
    print('TABLE',e.dxf.handle,e.dxf.insert, e.dxf.get('n_rows'), e.dxf.get('n_cols'))
for e in msp.query('TEXT MTEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    tl=t.lower()
    if any(k in tl for k in ['спецификац','грунт','окраш','краск','лист','масса','итого','всего','гост']):
        print(e.dxftype(),e.dxf.handle,[round(v) for v in e.dxf.insert][:2],t[:150].replace('\n',' | '))
