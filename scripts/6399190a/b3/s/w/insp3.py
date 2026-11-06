import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1])
for bn in ['ОК-1','оси-1']:
    b=d.blocks[bn]; c=collections.Counter((e.dxftype(),e.dxf.layer) for e in b); print(bn,len(b),c.most_common(15))
b=d.blocks['ОК-1']
for e in b:
    if e.dxftype()=='LWPOLYLINE': print('OK pl',[(round(p[0]),round(p[1])) for p in e.get_points()])
    elif e.dxftype()=='INSERT': print('OK ins',e.dxf.name)
b=d.blocks['оси-1']
for e in b:
    if e.dxftype() in('TEXT','MTEXT','ATTRIB'):
        print('T',[round(v) for v in e.dxf.insert][:2],(e.dxf.text if e.dxftype()!='MTEXT' else e.text)[:40])
    elif e.dxftype()=='INSERT':
        print('I',e.dxf.name,[round(v) for v in e.dxf.insert][:2],[ (a.dxf.tag,a.dxf.text) for a in e.attribs])
