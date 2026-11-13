import fitz,sys
from shapely.geometry import LineString,box
d=fitz.open('km.pdf')
for i in [2,3,4,5,6,7]:
    p=d[i]; W,H=p.rect.width,p.rect.height
    segs=[]
    for dr in p.get_drawings():
        w=dr.get('width') or 0
        for it in dr['items']:
            if it[0]=='l': segs.append((it[1],it[2],w))
            elif it[0]=='re':
                r=it[1]; 
                for a,b in [((r.x0,r.y0),(r.x1,r.y0)),((r.x1,r.y0),(r.x1,r.y1)),((r.x1,r.y1),(r.x0,r.y1)),((r.x0,r.y1),(r.x0,r.y0))]: segs.append((fitz.Point(a),fitz.Point(b),w))
            elif it[0]=='qu':
                q=it[1]; pts=[q.ul,q.ur,q.lr,q.ll]
                for k in range(4): segs.append((pts[k],pts[(k+1)%4],w))
    print('=== page',i+1,len(segs))
    words=p.get_text('words')
    seen=set()
    for w in words:
        x0,y0,x1,y1,t=w[:5]
        h=y1-y0; wd=x1-x0
        # shrink
        bx=box(x0+wd*0.04,y0+h*0.28,x1-wd*0.04,y1-h*0.28)
        hits=[]
        for a,b,wi in segs:
            if max(a.x,b.x)<bx.bounds[0] or min(a.x,b.x)>bx.bounds[2] or max(a.y,b.y)<bx.bounds[1] or min(a.y,b.y)>bx.bounds[3]: continue
            ls=LineString([(a.x,a.y),(b.x,b.y)])
            if ls.length<0.3: continue
            if ls.intersects(bx):
                hits.append((round(ls.length,1),round(wi,2)))
        # filter: text underlines tiny
        if hits:
            key=(t,round(x0),round(y0))
            if key in seen: continue
            seen.add(key)
            print(' ',ascii(t),[round(v) for v in (x0,y0,x1,y1)],hits[:4])
