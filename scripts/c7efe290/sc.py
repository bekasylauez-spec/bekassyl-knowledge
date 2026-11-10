import ezdxf,json,re,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf");msp=d.modelspace()
fr=json.load(open("D:/_claude_work/v113/ozh/frames.json",encoding='utf-8'))
T=[]
for e in msp:
    if e.dxftype()=='TEXT': T.append((e.dxf.insert.x,e.dxf.insert.y,e.dxf.text,e.dxf.height))
    elif e.dxftype()=='MTEXT': T.append((e.dxf.insert.x,e.dxf.insert.y,e.plain_text(),e.dxf.char_height))
D=[(e.dxf.get('dimstyle'),(e.dxf.get('text_midpoint') or e.dxf.defpoint)) for e in msp if e.dxftype()=='DIMENSION']
print([ (s.dxf.name,s.dxf.get('dimscale'),s.dxf.get('dimlfac'),s.dxf.get('dimtxt')) for s in d.dimstyles])
res={}
for f in fr:
    X0,Y0,X1,Y1=f['x0'],f['y0'],f['x0']+f['w'],f['y0']+f['h']
    sc=collections.Counter()
    for x,y,t,h in T:
        if X0<=x<=X1 and Y0<=y<=Y1:
            for m in re.findall(r'(?:^|[^\d])(1\s*:\s*\d+)',t): sc[m.replace(' ','')]+=1
    ds=collections.Counter(s for s,p in D if X0<=p.x<=X1 and Y0<=p.y<=Y1)
    res[f['n']]=(dict(sc),dict(ds))
    print(f['n'],f['sttx'][:2],dict(sc),dict(ds))
json.dump(res,open("D:/_claude_work/v113/ozh/scales.json","w"))
