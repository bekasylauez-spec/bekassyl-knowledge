import ezdxf,sys,collections,re
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
res=collections.defaultdict(list)
for e in ms.query('INSERT'):
    if 'AXIS' in e.dxf.name.upper() or 'ОСИ' in e.dxf.name.upper() or 'ОК' in e.dxf.name.upper():
        at={a.dxf.tag:a.dxf.text for a in e.attribs}
        res[e.dxf.name].append(([round(v) for v in e.dxf.insert][:2],round(e.dxf.rotation),at))
for k,v in res.items():
    print(k,len(v))
    for x in v[:400]: print('  ',x)
