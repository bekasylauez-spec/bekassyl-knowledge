import sys,struct,collections
sys.path.insert(0,r'D:/РАБОЧКА/КМ Чертеж Claude/src'); import lir_geom
d=open('v3.lir','rb').read()
m=lir_geom.read('v3.lir'); nodes=m['nodes']; bars=m['bars']
print(len(nodes),len(bars))
xs=sorted(set(round(n[0],2) for n in nodes)); ys=sorted(set(round(n[1],2) for n in nodes)); zs=sorted(set(round(n[2],3) for n in nodes))
print('X',len(xs),xs[:60]); print('Y',ys); print('Z',zs)
def kind(b):
    a,c=nodes[b[0]-1],nodes[b[1]-1]
    dx,dy,dz=[abs(c[i]-a[i]) for i in range(3)]
    if dx<1e-3 and dy<1e-3: return 'V'
    if dz<1e-3: return 'Hx' if dy<1e-3 else ('Hy' if dx<1e-3 else 'Hd')
    return 'I'
for off,stride,fmt in ((1526790,2,'B'),(1529526,2,'B'),(1526636,4,'<H')):
    vals=[struct.unpack_from(fmt,d,off+k*stride)[0] for k in range(len(bars))]
    c=collections.defaultdict(collections.Counter)
    for v,b in zip(vals,bars): c[v][kind(b)]+=1
    print(off,{k:dict(v) for k,v in sorted(c.items())})
