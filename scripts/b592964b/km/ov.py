import ezdxf,sys,collections,re
sys.stdout.reconfigure(encoding='utf-8')
doc=ezdxf.readfile(sys.argv[1]); msp=doc.modelspace()
c=collections.Counter(e.dxftype() for e in msp); print(c.most_common(12))
ins=collections.Counter(e.dxf.name for e in msp.query('INSERT')); print(ins.most_common(15))
print('layouts',[l.name for l in doc.layouts][:60])
kw=re.compile(sys.argv[2],re.I)
out=[]
for e in msp.query('TEXT MTEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if kw.search(t):
        p=e.dxf.insert; out.append((round(p.x),round(p.y),t.replace('\n',' | ')[:90]))
for o in sorted(out,key=lambda o:(round(o[1]/-30000),o[0]))[:150]: print(o)
