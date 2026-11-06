import gx, json
m=gx.tagmap(); inv={v:k[2:] for k,v in m.items() if k.startswith('A:')}
INV={}
for l in open(gx.S+r'\an\list_all.txt',encoding='utf-8-sig'):
    r=l.rstrip('\n').split('\t')
    if r[0] not in ('L','N') or r[2] not in inv: continue
    oh=inv[r[2]]
    if r[0]=='L': e=[float(v)-(3e6 if i%2==0 else 0) for i,v in enumerate(r[4][1:].split(','))]
    else: x,y=map(float,r[4].split(',')); e=[x-3e6,y,x-3e6,y]
    INV[oh]=dict(t=r[1],lay=r[3],e=e,pts=r[5:])
json.dump(INV,open(gx.S+r'\an\inv.json','w'),ensure_ascii=False)
G=lambda x: x+404751   # analog x -> galaxy sheet-1 x
def show(name,hs):
    print(name,[ (h, round(G(INV[h]['e'][0])), round(INV[h]['e'][1]+44140), round(G(INV[h]['e'][2])), round(INV[h]['e'][3]+44140)) for h in sorted(hs,key=lambda h:INV[h]['e'][0])])
show('cols',['40159B','4018B7','4018BA','4018BD','4018C0','4018C3'])
show('outl',['40159C','402404','403897','403898','403899'])
show('ax',['401290','401291','401295','401299','40129D','4012A1'])
show('axdim',['401296','40129A','40129E','4012A2','4012A5','401292'])
