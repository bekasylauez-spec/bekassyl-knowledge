import ezdxf,sys,re
doc=ezdxf.readfile(sys.argv[1])
for e in doc.modelspace().query('DIMENSION'):
    t=e.dxf.get('text','')
    try: m=float(e.get_measurement())
    except Exception: continue
    nums=re.findall(r"\d+(?:[.,]\d+)?",t)
    if t not in ('','<>') and nums and abs(float(nums[-1].replace(',','.'))-m)>2:
        print('OVR',round(m,1),repr(t),e.dxf.layer,[round(c) for c in e.dxf.defpoint][:2])
    elif round(m) in (2100,1800,2000,2200) :
        print('DIM',round(m,1),repr(t),[round(c) for c in e.dxf.defpoint][:2])
