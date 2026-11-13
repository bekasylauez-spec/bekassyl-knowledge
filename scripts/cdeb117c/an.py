import ezdxf,sys,collections
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf'); msp=doc.modelspace()
X0,X1,Y0,Y1=1050000,1109400,95516,137516
def inw(p): return X0<=p[0]<=X1 and Y0<=p[1]<=Y1
cnt=collections.Counter()
rows=[]
for e in msp:
    t=e.dxftype()
    try:
        if t in('TEXT','MTEXT'):
            p=e.dxf.insert
            if not inw(p):continue
            h=e.dxf.height if t=='TEXT' else e.dxf.char_height
            txt=e.dxf.text if t=='TEXT' else e.plain_text()
            rows.append((t,round(p[0]),round(p[1]),h,e.dxf.style,e.dxf.layer,txt.replace('\n','|')[:60]))
        elif t=='DIMENSION':
            p=e.dxf.defpoint
            if not inw(p):continue
            cnt['dim',e.dxf.dimstyle]+=1
        elif t=='INSERT':
            p=e.dxf.insert
            if inw(p): cnt['ins',e.dxf.name[:30]]+=1
        elif t in('LINE','LWPOLYLINE','HATCH','CIRCLE','SOLID'):
            p=e.dxf.start if t=='LINE' else (e.dxf.center if t=='CIRCLE' else None)
            if p is not None and inw(p): cnt[t,e.dxf.layer]+=1
    except Exception as ex: cnt['err',t]+=1
for r in sorted(rows,key=lambda r:(-r[2],r[0])): print(r)
print(cnt)
print(doc.header.get('$DIMSCALE'))
