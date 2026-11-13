import io, collections, re, math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\q20\\"
out=io.open(D+'a11_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
Z=[l.rstrip('\n').split('\t') for l in io.open(D+'zfight2.tsv',encoding='utf-8')]
P('candidate rows',len(Z))
def parse(loops):
    res=[]
    for lp in loops.split('|'):
        pts=[tuple(map(float,p.split(';'))) for p in lp.split(' ') if p]
        res.append(np.array(pts))
    return res
def poly2d(loops,e1,e2):
    rings=[]
    for arr in loops:
        if len(arr)<3: continue
        rings.append([(float(np.dot(p,e1)),float(np.dot(p,e2))) for p in arr])
    if not rings: return None
    # largest ring is outer; others holes
    polys=[Polygon(r) for r in rings]
    polys=[p.buffer(0) for p in polys]
    outer=max(polys,key=lambda p:p.area)
    for p in polys:
        if p is not outer: outer=outer.difference(p)
    return outer
def part(n):
    n2=re.sub(r' - [\w\-+А-Яа-я]+$','',n)
    for k in ('шов','заглушка','вставка','гусет','фасонка','болт','гайка','шайба','ребро','оголовок','диафрагма','кронштейн','фланец','накладка','прокладка','плита','траверса','подливка','анкер','лист','тартпа','рельс','уголок','швеллер','брус','косынка','рыбка','тіреуіш','подколонник','тірек','жота'):
        if k in n2: return k
    return 'каркас '+n.split()[0] if n and n[0] in 'КБПРСГ' else 'other'
real=[]; cnt=collections.Counter(); ex={}
for z in Z:
    cn,ak,al,an,aid,am,bk,bl,bn,bid,bm,nx,ny,nz,area,ex_,ey_,ez_,la,lb=z
    n=np.array([float(nx),float(ny),float(nz)]); n=n/np.linalg.norm(n)
    h=np.array([1,0,0]) if abs(n[0])<0.9 else np.array([0,1,0])
    e1=np.cross(n,h); e1/=np.linalg.norm(e1); e2=np.cross(n,e1)
    try:
        pa=poly2d(parse(la),e1,e2); pb=poly2d(parse(lb),e1,e2)
        if pa is None or pb is None: continue
        a=pa.intersection(pb).area
    except Exception as e:
        P('ERR',e); continue
    if a>1.0:
        real.append((a,an,bn,aid,bid,cn))
        k=tuple(sorted([part(an) if not an.startswith(('К','Б','Р','С','Г','П')) or ' - ' in an else 'каркас '+an.split()[0], part(bn) if not bn.startswith(('К','Б','Р','С','Г','П')) or ' - ' in bn else 'каркас '+bn.split()[0]]))
        cnt[k]+=1; ex.setdefault(k,[]).append((round(a,1),an,bn,aid,bid))
P('real overlap area >1 mm2 (shapely polygons, same-direction coplanar):',len(real),' pairs; distinct element pairs:',len(set((r[3],r[4]) for r in real)))
P('area>50 mm2:',sum(1 for r in real if r[0]>50),' area>500:',sum(1 for r in real if r[0]>500))
for k,v in cnt.most_common(30):
    e=sorted(ex[k],reverse=True)[0]
    P(v,k,'| max area',e[0],'|',e[1][:60],'<->',e[2][:60],e[3],e[4])
out.close()