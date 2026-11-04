import ezdxf,sys
from ezdxf.proxygraphic import ProxyGraphic
d=ezdxf.readfile(sys.argv[1])
for h in sys.argv[2:]:
    e=d.entitydb.get(h)
    if e is None: print(h,'none'); continue
    try:
        pg=ProxyGraphic(e.proxy_graphic,d)
        ts=[ (x.dxftype(), getattr(x.dxf,'text',None) or (x.plain_text() if x.dxftype()=='MTEXT' else '')) for x in pg.virtual_entities() if x.dxftype() in('TEXT','MTEXT')]
        print(h,e.dxftype(),ts)
    except Exception as ex: print(h,ex)
