import ezdxf
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf'); msp=doc.modelspace()
for e in msp.query('INSERT'):
    p=e.dxf.insert
    if 1050000<=p[0]<=1109400 and 95516<=p[1]<=137516:
        print(e.dxf.name,p,e.dxf.xscale,[(a.dxf.tag,a.dxf.text) for a in e.attribs])
        for v in doc.blocks[e.dxf.name]:
            if v.dxftype() in('TEXT','MTEXT'): print('  ',v.dxftype(),(v.dxf.text if v.dxftype()=='TEXT' else v.plain_text())[:70])
for e in msp:
    if e.dxftype() in('TEXT','MTEXT'):
        p=e.dxf.insert
        if 1050000<=p[0]<=1109400 and 95516<=p[1]<=137516 and e.dxftype()=='MTEXT' and 'Общие' in e.plain_text(): print(e.plain_text())
