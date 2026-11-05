import ezdxf, sys, json, ezdxf.bbox as BB
out={}
for n in sys.argv[1:]:
    d=ezdxf.readfile(n+'.dxf'); m=d.modelspace(); fr=[]
    for e in m.query('ACAD_PROXY_ENTITY'):
        try: b=BB.extents([e],fast=True)
        except Exception: continue
        if not b.has_data: continue
        w,h=b.size.x,b.size.y
        for W,H in ((59400,42000),(42000,59400),(42000,29700),(29700,42000),(59400,84100),(84100,59400),(84100,118900)):
            for s in (0.25,0.5,1,2):
                if abs(w-W*s)<50 and abs(h-H*s)<50: fr.append([b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y,s])
    fr.sort(key=lambda r:(round(-r[1]/1000),r[0]))
    out[n]=fr; print(n,len(fr))
json.dump(out,open('frames.json','w'))
