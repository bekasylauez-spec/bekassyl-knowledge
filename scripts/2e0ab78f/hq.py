# hq.py sheetX0 h1 h2 ... : describe entities (dxf + geom dump) relative to sheet origin
import sys, ezdxf
X0=float(sys.argv[1]); Y0=600000.0; hs=[h.upper() for h in sys.argv[2:]]
G={}
for ln in open(r'D:\_claude_work\otst\s1\job\geom.txt',encoding='utf-8-sig'):
    f=ln.rstrip('\r\n').split('|')
    if len(f)>1 and f[1] in hs: G.setdefault(f[1],[]).append(f)
doc=ezdxf.readfile(r'D:\_claude_work\otst\s1\job\live.dxf')
for h in hs:
    e=doc.entitydb.get(h)
    print('##',h, e.dxftype() if e else None, e.dxf.layer if e else '')
    if e is not None and e.dxftype()=='LWPOLYLINE':
        print('  pts', [(round(p[0]-X0),round(p[1]-Y0)) for p in e.get_points('xy')][:12])
    if e is not None and e.dxftype() in('MTEXT','TEXT'):
        print('  ', e.dxf.insert[0]-X0, e.dxf.insert[1]-Y0, e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text)
    for f in G.get(h,[])[:14]:
        if f[0]=='S': print('  S', f[2], round(float(f[3])-X0),round(float(f[4])-Y0),round(float(f[5])-X0),round(float(f[6])-Y0))
        else: print('  T', f[2], [round(float(v)-(X0 if i%2==0 else Y0)) for i,v in enumerate(f[3:7])], f[7])
