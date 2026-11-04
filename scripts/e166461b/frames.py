import sys, logging; logging.disable(logging.CRITICAL)
import ezdxf
from ezdxf.proxygraphic import ProxyGraphic
from ezdxf import bbox
f=sys.argv[1]
L=open(f,encoding='cp1251',errors='replace').read().split('\n'); L=[x.strip() for x in L]
cls=[]; i=0
while i<len(L)-1:
    if L[i]=='0' and L[i+1]=='CLASS':
        j=i+2; name=None
        while L[j]!='0':
            if L[j]=='1': name=L[j+1]
            j+=2
        cls.append(name); i=j
    elif L[i]=='2' and L[i+1]=='ENTITIES': break
    else: i+=1
fr=set(); i=0
while i<len(L)-1:
    if L[i]=='0' and L[i+1]=='ACAD_PROXY_ENTITY':
        j=i+2; h=None; cid=None
        while L[j]!='0':
            if L[j]=='5' and h is None: h=L[j+1]
            if L[j]=='91' and cid is None: cid=int(L[j+1])
            j+=2
        if cid and 0<=cid-500<len(cls) and cls[cid-500]=='SPDSFORMAT': fr.add(h)
        i=j
    else: i+=1
d=ezdxf.readfile(f); m=d.modelspace()
out=[]
for e in m:
    if e.dxf.handle in fr:
        try:
            ve=list(ProxyGraphic(e.proxy_graphic,d).virtual_entities()); b=bbox.extents(ve)
            out.append((round(b.extmin.x),round(b.extmin.y),round(b.extmax.x),round(b.extmax.y)))
        except Exception as ex: out.append(('err',e.dxf.handle))
# titles: mtext near frames
for b in sorted(out, key=lambda t: (t[1] if isinstance(t[1],int) else 0, t[0] if isinstance(t[0],int) else 0)):
    tt=[]
    if isinstance(b[0],int):
        for e in m.query('MTEXT TEXT'):
            p=e.dxf.insert
            if b[0]<p[0]<b[2] and b[1]<p[1]<b[3]:
                t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
                if len(t)>12 and any(k in t for k in ('Схема','Разрез','Спецификац','Стена','Опалуб','Армир','Плита','Узел','Ведомость')): tt.append(t[:70].replace('\n',' '))
    print(b, (b[2]-b[0], b[3]-b[1]) if isinstance(b[0],int) else '', tt[:4])
