import ezdxf,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
print(d.layouts.names_in_taborder())
for l in d.layouts:
    print(l.name, l.dxf.get('paper_width'), len(l), [ (e.dxftype()) for e in l][:5])
ins=collections.Counter(e.dxf.name for e in msp if e.dxftype()=='INSERT')
for n,c in ins.most_common(25):
    b=d.blocks.get(n); print(n,c,len(b),collections.Counter(e.dxftype() for e in b).most_common(3))
print([ (e.dxftype(),e.dxf.layer) for e in msp if e.dxftype() in('ACAD_TABLE','OLE2FRAME')])
print(collections.Counter(e.dxf.layer for e in msp).most_common(30))
print(list(d.header.get('$EXTMIN')),list(d.header.get('$EXTMAX')))
