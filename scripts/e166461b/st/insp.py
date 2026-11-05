import ezdxf,ezdxf.bbox,json,collections,sys
F=json.load(open('frames.json'))[sys.argv[1]]; k=int(sys.argv[2])
x0,y0,x1,y1,s=F[k]; print('frame',x0,y0,x1,y1,s)
d=ezdxf.readfile(sys.argv[1]+'.dxf'); m=d.modelspace()
c=collections.Counter(); dims=collections.Counter(); hs=[]
for e in m:
    try:
        b=ezdxf.bbox.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    if b.extmin.x>=x0-1 and b.extmax.x<=x1+1 and b.extmin.y>=y0-1 and b.extmax.y<=y1+1:
        t=e.dxftype(); c[(t,e.dxf.layer)]+=1
        if t=='DIMENSION':
            o=e.override(); dims[(e.dxf.dimstyle, o.get('dimlfac',1), o.get('dimscale',None))]+=1
        hs.append((e.dxf.handle,t,round(b.extmin.x-x0),round(b.extmin.y-y0),round(b.size.x),round(b.size.y),getattr(e.dxf,'name','') if t=='INSERT' else (e.dxf.get('text','')[:30] if t in('TEXT','MTEXT') else '')))
for k2,v in sorted(c.items(),key=lambda a:-a[1]): print(k2,v)
print(dims)
json.dump(hs,open('ents_%s_%s.json'%(sys.argv[1],sys.argv[2]),'w'),ensure_ascii=False)
