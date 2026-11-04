import ezdxf,sys,collections
for i in range(1,5):
    d=ezdxf.readfile(sys.argv[1]+f'/ar/a{i}.dxf')
    m=d.modelspace()
    c=collections.Counter((e.dxftype(),e.dxf.layer) for e in m)
    print('== a%d'%i, d.header.get('$INSUNITS'), 'layouts',[l.name for l in d.layouts])
    try:
        from ezdxf import bbox
        b=bbox.extents(m); print('ext',b.extmin,b.extmax)
    except Exception as ex: print(ex)
    for k,v in sorted(c.items(),key=lambda x:-x[1])[:40]: print(' ',v,k)
    print(' blocks:',[b.name for b in d.blocks if not b.name.startswith('*')][:40])
