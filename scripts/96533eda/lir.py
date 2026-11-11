import struct,sys,collections,math
d=open(sys.argv[1],'rb').read()
nn=195; ne=306
N=[struct.unpack_from('<3d',d,138+28*i) for i in range(nn)]
E=[struct.unpack_from('<3i',d,5594+38*i) for i in range(ne)]
S=struct.unpack_from('<%dH'%ne,d,94995)
names=['40Ш1','□250х6','50Б1','□100х3','□100х5(2012)','□100х5(2003)','Плита','Гн[250х80х5','30Б1','30М']
print('nodes',nn,'elems',ne,'end',5594+38*ne, d[5594+38*ne:5594+38*ne+20])
agg=collections.defaultdict(lambda:[0,0.0,set()])
for (t,a,b),s in zip(E,S):
    L=math.dist(N[a],N[b]); g=agg[s]; g[0]+=1; g[1]+=L; g[2].add(round(N[a][2],3)); g[2].add(round(N[b][2],3))
for s in sorted(agg): g=agg[s]; print(s,names[s] if s<len(names) else '?',g[0],round(g[1],2),sorted(g[2]))
sup=[i for i,n in enumerate(N) if abs(n[2]+0.4)<1e-6]; print('supports',len(sup))
