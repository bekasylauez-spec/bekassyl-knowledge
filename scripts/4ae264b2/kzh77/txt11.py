import ezdxf,sys,re
from ezdxf.recover import readfile
doc,aud=readfile(sys.argv[1])
out=[]
def clean(s):
    return re.sub(r'\[A-Za-z][^;\]*;|[{}]|\P',' ',s).strip()
for lay in doc.layouts:
    for e in lay:
        t=e.dxftype()
        if t=='TEXT': out.append((lay.name,'T',e.dxf.insert.x,e.dxf.insert.y,e.dxf.text))
        elif t=='MTEXT': out.append((lay.name,'M',e.dxf.insert.x,e.dxf.insert.y,e.plain_text().replace(chr(10)," ")))
        elif t=='DIMENSION':
            try: m=e.get_measurement()
            except: m=None
            out.append((lay.name,'D',e.dxf.defpoint.x,e.dxf.defpoint.y,'%s|%s'%(e.dxf.text,m)))
        elif t=='INSERT':
            for a in e.attribs: out.append((lay.name,'A',e.dxf.insert.x,e.dxf.insert.y,e.dxf.name+':'+a.dxf.text))
for o in out: print('%s\t%s\t%.0f\t%.0f\t%s'%o)
