import sys,json,ezdxf
d=ezdxf.readfile('album.dxf');msp=d.modelspace()
sh=json.load(open('sheets.json'))
want=sys.argv[1:]
from collections import defaultdict
res=defaultdict(list)
for e in msp:
    t=e.dxftype()
    try:
        if t in('TEXT','MTEXT'):
            p=e.dxf.insert; x,y=p[0],p[1]
        elif t=='DIMENSION':
            p=e.dxf.defpoint; x,y=p[0],p[1]
        else: continue
    except: continue
    for k in want:
        x0,y0,x1,y1,_=sh[k]
        if x0<=x<=x1 and y0<=y<=y1:
            W=x1-x0;H=y1-y0
            fx=(x-x0)/W*100;fy=100-(y-y0)/H*100
            if t=='TEXT': s=e.dxf.text
            elif t=='MTEXT': s=e.plain_text().replace('\n','|')
            else:
                try: m=e.get_measurement()
                except: m='?'
                try: s='DIM meas=%s txt=%r'%(round(m,1) if not hasattr(m,'x') else m,e.dxf.text)
                except: s='DIM'
            res[k].append((round(fx,1),round(fy,1),t,s[:90]))
for k in want:
    print('=====',k)
    for r in sorted(res[k],key=lambda r:(r[2],r[0])): print(r)
