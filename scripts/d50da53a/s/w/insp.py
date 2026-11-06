import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
c=collections.Counter((e.dxftype(),e.dxf.layer) for e in ms); 
for k,v in c.most_common(60): print(v,k)
print('layouts',[l.name for l in d.layouts])
txt=[e for e in ms if e.dxftype() in('TEXT','MTEXT')]
for e in txt[:200]:
    t=e.dxf.text if e.dxftype()=='TEXT' else e.text
    p=e.dxf.insert; print('T',round(p.x),round(p.y),e.dxf.layer,t[:60].replace('\n',' '))
