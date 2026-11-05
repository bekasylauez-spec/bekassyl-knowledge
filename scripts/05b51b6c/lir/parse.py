import struct,collections,json,math,sys
b=open('obez.lir','rb').read()
N=2802; NE=3364
nodes=[struct.unpack_from('<ddd',b,138+28*i) for i in range(N)]
e0=138+28*N
els=[]
st=struct.unpack_from('<%dH'%NE,b,1290558)
for i in range(NE):
  r=struct.unpack_from('<8I3H',b,e0+38*i)
  nn=list(r[:8])
  k={0:2,1:3,2:4}[r[8]]
  els.append(dict(i=i+1,n=nn[:k],s=st[i]+1,f=r[8:]))
names={1:'ФП t1000',2:'Плита t200',3:'ЛФ 35x60',4:'Кол 60x60',5:'Кол 70x70',6:'Кол 90x70',7:'Кол 70x90',8:'Б 35x60',9:'Б 30x40',10:'Б 45x60',11:'Б 40x60',12:'Б 45x70',13:'Б 50x70',14:'Б 60x70',15:'Б 60x80',16:'Б 70x80',17:'Б 40x50',18:'Б 20x40',19:'Б 45x60b',20:'I сост 250x10/480x8',21:'Рандб 70x85',22:'I сост 250x10/300x6',23:'Тр140x4.5 XG1',24:'L100x7 Sc1',25:'?25',26:'[18П прогон',27:'□120x4 ГС',28:'□80x4 ГС'}
json.dump(dict(nodes=nodes,els=els,names=names),open('model.json','w'))
g=collections.defaultdict(list)
for e in els: g[e['s']].append(e)
for s in sorted(g):
  E=g[s]; nn=collections.Counter(len(e['n']) for e in E)
  pts=[nodes[j] for e in E for j in e['n']]
  xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; zs=[p[2] for p in pts]
  Lsum=sum(math.dist(nodes[e['n'][0]],nodes[e['n'][1]]) for e in E if len(e['n'])==2)
  bars=[e for e in E if len(e['n'])==2]
  print(s,names.get(s),len(E),dict(nn),'x %.2f..%.2f y %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys)),'z',sorted(set(round(z,2) for z in zs))[:8],'L=%.1f'%Lsum)
