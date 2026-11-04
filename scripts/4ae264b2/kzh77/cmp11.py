import re
from ezdxf.recover import readfile
doc,_=readfile(r'dxf/f11.dxf'); msp=doc.modelspace()
def vis(e):
    l=doc.layers.get(e.dxf.layer)
    return l is None or (l.is_on() and not l.is_frozen())
items=[]
for e in msp:
    if not vis(e): continue
    t=e.dxftype(); x=y=None
    if t=='TEXT': s=e.dxf.text; p=e.dxf.insert
    elif t=='MTEXT': s=e.plain_text(); p=e.dxf.insert
    elif t=='DIMENSION':
        o=e.dxf.text; 
        try: m=e.get_measurement(); m='%d'%round(m) if isinstance(m,float) else ''
        except: m=''
        s=o.replace('<>',m) if o else m; p=e.dxf.defpoint
    elif t=='INSERT':
        for a in e.attribs:
            if vis(a): items.append((e.dxf.insert.x,e.dxf.insert.y,'A',a.dxf.text))
        continue
    else: continue
    items.append((p.x,p.y,t[0],s))
# sheet bboxes guessed
sheets={'8.1':(60000,-118000,87000,-75000),'8.2':(88000,-118000,128000,-90000),'8.3':(129000,-118000,150000,-90000),'8.4':(150000,-118000,171500,-90000),'8.5':(172000,-118000,224000,-94000)}
pages={'8.1':119,'8.2':120,'8.3':121,'8.4':122,'8.5':123}
def norm(s): return re.sub(r'\s+','',s.replace('%%C','∅').replace('%%c','∅').replace('Ø','∅'))
for sh,(x0,y0,x1,y1) in sheets.items():
    pdf=open('txt/pages/p%03d.txt'%pages[sh],encoding='utf-8').read()
    pdfl=[norm(l) for l in pdf.split('\n') if l.strip()]
    pdfn=''.join(pdfl)
    ins=[i for i in items if x0<=i[0]<=x1 and y0<=i[1]<=y1]
    dx=''.join(norm(i[3]) for i in ins)
    print('==',sh,'dxf items',len(ins))
    for i in ins:
        k=norm(i[3])
        if k and k not in pdfn: print('  DXF-only %s %.0f %.0f %r'%(i[2],i[0],i[1],i[3][:100]))
    for l in pdfl:
        if l and l not in dx: print('  PDF-only %r'%l[:100])
# off-sheet visible items
print('== visible outside sheets')
for i in items:
    if not any(x0<=i[0]<=x1 and y0<=i[1]<=y1 for (x0,y0,x1,y1) in sheets.values()):
        print('  %s %.0f %.0f %r'%(i[2],i[0],i[1],i[3][:80]))
