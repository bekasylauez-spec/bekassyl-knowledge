import ezdxf,sys,re,pickle
n=sys.argv[1]
d=ezdxf.readfile(f"dx/{n}.dxf")
out=[]
def walk(lay,owner):
    for e in lay:
        t=e.dxftype()
        try:
            if t=='TEXT': out.append((owner,t,e.dxf.handle,e.dxf.insert.x,e.dxf.insert.y,e.dxf.text))
            elif t=='MTEXT': out.append((owner,t,e.dxf.handle,e.dxf.insert.x,e.dxf.insert.y,e.plain_text()))
            elif t=='ACAD_TABLE':
                p=e.dxf.insert
                out.append((owner,t,e.dxf.handle,p.x,p.y,'TABLE blk='+str(e.dxf.get('geometry',''))))
            elif t=='INSERT':
                for a in e.attribs: out.append((owner,'ATTRIB',a.dxf.handle,a.dxf.insert.x,a.dxf.insert.y,a.dxf.text))
        except Exception as ex: pass
walk(d.modelspace(),'MS')
for b in d.blocks:
    if b.name.startswith('*Paper') or b.name.startswith('*Model'): continue
    walk(b,'B:'+b.name)
pickle.dump(out,open(f"dx/{n}_txt.pkl",'wb'))
print(len(out))
types={}
for e in d.modelspace(): types[e.dxftype()]=types.get(e.dxftype(),0)+1
print(types)
print([l.name for l in d.layouts][:80])
