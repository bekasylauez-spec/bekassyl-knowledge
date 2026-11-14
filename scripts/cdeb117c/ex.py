import ezdxf, re, sys
doc = ezdxf.readfile(r'D:\_claude_work\maftun\src\alb.dxf')
msp = doc.modelspace()
SH = {'fv':(1050000,59400),'s3':(1109400,59400),'s5':(1168800,42000),'s6':(1210800,59400),'s2':(1270200,42000),'s1':(1312200,59400)}
Y0=95516
out = {k:[] for k in SH}
def pos(e):
    try:
        return e.dxf.insert
    except Exception: return None
def put(x,y,t):
    for k,(x0,w) in SH.items():
        if x0<=x<=x0+w and Y0<=y<=Y0+42000: out[k].append((round(x-x0),round(y-Y0),t))
for e in msp:
    tp=e.dxftype()
    if tp in ('TEXT','MTEXT'):
        p=pos(e); t=e.plain_text() if tp=='MTEXT' else e.dxf.text
        put(p.x,p.y,t)
    elif tp=='INSERT':
        p=e.dxf.insert
        for a in e.attribs: put(p.x,p.y,'[ATT]'+a.dxf.text)
        try:
            for v in e.virtual_entities():
                if v.dxftype() in ('TEXT','MTEXT'):
                    q=v.dxf.insert; put(q.x,q.y,'[blk]'+(v.plain_text() if v.dxftype()=='MTEXT' else v.dxf.text))
        except Exception: pass
    elif tp=='DIMENSION':
        try:
            p=e.dxf.text_midpoint; put(p.x,p.y,'[dim]'+str(e.dxf.text)+'|'+str(round(e.get_measurement(),1)))
        except Exception: pass
import json
json.dump(out, open('txt.json','w',encoding='utf8'), ensure_ascii=False)
for k in out: print(k, len(out[k]))
