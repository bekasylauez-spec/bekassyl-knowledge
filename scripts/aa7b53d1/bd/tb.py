import ezdxf,re
doc=ezdxf.readfile('w.dxf')
msp=doc.modelspace()
for e in msp.query('ACAD_TABLE'):
    ins=e.dxf.insert
    out=[]
    try:
        ves=list(e.virtual_entities())
    except Exception as ex:
        ves=[]; print('ERR',ex)
    for m in ves:
        if m.dxftype() in('MTEXT','TEXT'):
            p=m.dxf.insert; t=m.plain_text() if m.dxftype()=='MTEXT' else m.dxf.text
            out.append((round(-p.y,-1),round(p.x),t.replace('\n',' ')))
    out.sort()
    print('TABLE',e.dxf.handle,round(ins.x),round(ins.y))
    rows={}
    for y,x,t in out: rows.setdefault(y,[]).append(t)
    for y in sorted(rows): print('   ',' | '.join(rows[y])[:300])
    print()
