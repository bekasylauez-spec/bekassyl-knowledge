import ab, json, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
S=json.load(open('w/sheets2.json'))
NODES={'390C0C':('А',2),'390C0D':('Б',3),'390C0E':('В',2),'390C2A':('А',2),'390C2B':('Б',3),'390C2C':('В',2)}
C={'390C0C':(-686779,-1743838),'390C0D':(-686779,-1737838),'390C0E':(-686779,-1731838),'390C2A':(-665379,-1743838),'390C2B':(-665379,-1737838),'390C2C':(-665379,-1731838)}
ops=[]
for h,(row,k) in NODES.items():
    ops.append({'t':'explode','h':h})
ONLY=['LINE','LWPOLYLINE','DIMENSION']
for h,(row,k) in NODES.items():
    x,y=C[h]
    up={'А':400,'В':0,'Б':550}[row]; dn={'А':0,'В':400,'Б':550}[row]
    if up: ops.append({'t':'stretchwin','win':[x-260,y+170,x+260,y+230],'d':[0,up],'only':ONLY})
    if dn: ops.append({'t':'stretchwin','win':[x-260,y-230,x+260,y-170],'d':[0,-dn],'only':ONLY})
r=ab.run(ops+[{'t':'save'}],'v36',600); print(r[-700:])
# marks
ab.run([{'t':'notelist'}],'nl',300)
v2=[];v3=[]
for l in open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8-sig'):
    p=l.rstrip('\n').split('\t')
    if not l.startswith('N\t') or 'Bn-1' not in p[3]+p[4]: continue
    pts=[tuple(map(float,q.split(','))) for q in p[9:] if q and not q.startswith('E')]
    for h,(row,k) in NODES.items():
        x,y=C[h]
        if any(abs(a-x)<450 and abs(b-y)<450 for a,b in pts): (v3 if k==3 else v2).append(p[1]); break
print('v2',v2,'v3',v3)
print(ab.run([{'t':'mcrep','win':S['3.6'] if '3.6' in S else [-691503.1,-1749172.3,-661803.1,-1728172.3],'pairs':[['Bn-1','Bn-2']],'only':v2},
              {'t':'mcrep','win':[-691503.1,-1749172.3,-661803.1,-1728172.3],'pairs':[['Bn-1','Bn-3']],'only':v3},{'t':'save'}],'mc36',300)[-300:])
