import ezdxf,sys
d=ezdxf.readfile(sys.argv[1])
msp=d.modelspace()
print(d.entitydb[ '5DE889'].plain_text())
for h in sys.argv[2:]:
    e=d.entitydb[h]
    bn=e.dxf.geometry
    print('==',h,bn)
    blk=d.blocks.get(bn)
    rows=[]
    for x in blk:
        if x.dxftype() in('MTEXT','TEXT'):
            t=x.plain_text() if x.dxftype()=='MTEXT' else x.dxf.text
            rows.append((round(-x.dxf.insert[1]),round(x.dxf.insert[0]),t.replace('\n',' ')))
    rows.sort()
    cur=None
    for y,xx,t in rows:
        if cur is None or abs(y-cur)>40: print(); cur=y
        print(f'[{xx}] {t}',end='  ')
    print()
