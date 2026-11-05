import spec, ab, json, math
from spec import KG, f2
KG[25]=math.pi/4*0.025**2*7850; KG[28]=math.pi/4*0.028**2*7850
SH=json.load(open('sheets.json'))
def win(s,p=50): a,b,c,d=SH[s]; return [a-p,b-p,c+p,d+p]
O=[]; rep=[]
# 4.1 Км-1
op,t,bd=spec.rowops('38104E',[(1,8,'A240',None,60,0.5839844),(2,8,'A240',None,60,0.4419341),(3,16,'A500',None,2,1.2468855),(4,16,'A500',None,2,1.5625528),
 (5,28,'A500',5300,8,None),(6,28,'A500',2680,8,None),(7,28,'A500',2580,4,None),(9,28,'A500',280,32,None),(10,10,'A500',None,8,1.8249511)],(0,12),
 [(12,12,'1.38'),(5,3,'28'),(6,3,'28'),(7,3,'28'),(9,3,'28'),(9,0,'Н2')])
O.append(op); O.append(spec.steel('381085',6,[(1,('A240',6)),(2,('A240',8)),(3,('itogo','A240')),(4,('A500',10)),(5,('A500',16)),(6,('A500',28)),(7,('itogo','A500')),(8,('all',))],bd))
O.append({'t':'tset','h':'381085','cells':[[5,6,'%%C28']]}); rep.append(('4.1 Км-1',t))
# 3.7 выпуск Вп-1
x=1.1679687+0.8838682; p3=4*1.1*KG[28]; p4=4*1.7*KG[28]; vp=x+p3+p4
cells=[[8,3,'28'],[9,3,'28'],[8,11,f2(1.1*KG[28])],[8,12,f2(p3)],[9,11,f2(1.7*KG[28])],[9,12,f2(p4)],[7,12,f2(vp)],[2,11,f2(vp)],[2,12,f2(33*vp)]]
wall=823.47+1513.72; tot=33*vp+wall; cells.append([0,12,f2(tot)])
O.append({'t':'tset','h':'3807BA','cells':cells})
a240=33*x; a12=wall; a28=33*(p3+p4)
O.append({'t':'tset','h':'3807BC','cells':[[5,6,'%%C28'],[6,1,'0.00'],[6,2,f2(a240)],[6,3,f2(a240)],[6,4,f2(a12)],[6,5,'0.00'],[6,6,f2(a28)],[6,7,f2(a12+a28)],[6,8,f2(tot)]]}); rep.append(('3.7 выпуск',tot))
# 6.1 / 6.2 Рм
for h,hv,q1,qx,qn in (('382757','382759',371.27,391,54),('38327A','38327C',73.15,75,6)):
    op,t,bd=spec.rowops(h,[(1,8,'A240',None,qx,0.5839844),(2,16,'A500',None,6,1.2942356),(3,25,'A500',None,q1,KG[25]),(4,25,'A500',250,qn,None)],(0,12),[(3,3,'25'),(4,3,'25'),(4,0,'Н3')])
    op['cells']=[c for c in op['cells'] if not (c[0]==3 and c[1]==10)]  # keep пог.м qty text
    op['cells'].append([3,10,'%.2f'%q1])
    O.append(op); O.append(spec.steel(hv,6,[(1,('A240',8)),(2,('A240',10)),(3,('itogo','A240')),(4,('A500',12)),(5,('A500',14)),(6,('A500',16)),(7,('A500',25)),(8,('itogo','A500')),(9,('all',))],bd))
    O.append({'t':'tset','h':hv,'cells':[[5,7,'%%C25']]}); rep.append((h,t))
# SPDS notes
O.append({'t':'mcrep','win':win('4.1'),'pairs':[['%%C20','%%C28'],['Н5','Н2']]})
O.append({'t':'mcrep','win':win('3.7'),'pairs':[['(∅20)','(∅28)'],['(%%C20)','(%%C28)']]})
for s in ('6.1','6.2'): O.append({'t':'mcrep','win':win(s),'pairs':[['Н5','Н3']]})
O.append({'t':'mcrep','win':win('3.2'),'pairs':[['(ф12)','(ф16)'],['(ф14)','(ф16)']]})
O.append({'t':'mcrep','win':win('3.3'),'pairs':[['(∅12)','(∅16)']]})
O.append({'t':'mcrep','win':win('3.5'),'pairs':[['(∅12)','(∅16)']],'only':['37FC04','37FC05','37FC09','37FC0A','37FC0E','37FC0F','37FB37','37FC47']})
for r in rep: print(r[0],round(r[1],2))
import os
ab.run(O,'phaseA'); print(open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8').read()[-1500:])
