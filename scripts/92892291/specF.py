import spec,ab,os
from spec import KG,f2
k=312/144
op,t,bd=spec.rowops('37FCCB',[(3,8,'A240',None,round(551*k),0.5760927),(4,12,'A500',None,24,1.7223593),(5,16,'A500',None,1012.82*k,KG[16]),
 (6,16,'A500',None,1211,KG[16]*3.04),(7,12,'A500',None,623,1.1470558),(8,16,'A500',None,76,KG[16]*4.84),(9,16,'A500',None,237,KG[16]*4.88),(10,16,'A500',None,457,KG[16]*3.08)],
 (2,12),[(12,12,'70.80'),(13,12,'29.80')]+[(r,3,'16') for r in (5,6,8,9,10)])
op['cells']=[c for c in op['cells'] if not (c[0]==5 and c[1]==10)]+[[5,10,'%.2f'%(1012.82*k)]]
O=[op,spec.steel('37FCCC',6,[(1,('A240',8)),(2,('itogo','A240')),(3,('A500',12)),(4,('A500',16)),(5,('itogo','A500')),(6,('all',))],bd),
   {'t':'tset','h':'37FCCC','cells':[[5,4,'%%C16']]},
   {'t':'trows','h':'34209C','mode':'del','at':4,'n':1},{'t':'mcrep','win':[-1552853,-1749222,-1463653,-1707122],'pairs':[['Фм-2','Фм-1']]}]
print(round(t,2))
ab.run(O,'specF'); print(open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8').read()[-200:])
