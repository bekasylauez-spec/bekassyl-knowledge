import sys,struct,collections; sys.path.insert(0,'.')
from lirparse import load
d,nodes,els,end=load()
N=len(els)
stf=[struct.unpack_from('<H',d,1517340+2*k)[0] for k in range(N)]
NAMES=['К 60Ш2','К низ 60Ш3','Б 40Б1','Б1 30Б1','ФФ вп 20Ш1','вс □100x3','с □100x3','ПБ сварн','КН 40Ш1','рс □100x5','ВС □160x5','ВС1 □100x5','Т 70Б1','а 30Б1','Плита','Т1 45Ш1','а1 25Б1','?? [27П','СТ □200x6','К2 короб350x12','Т1 50Ш2','ФФ нп □120x5','ФФ р □120x5','ФФ р1 □100x3','СФ 40Ш2','для ветра']
ROWS={0:'A',6:'B',12:'C',18:'D',24:'E',27:'F',33:'G',36:'H',42:'I',48:'K',54:'L',60:'M'}
def ax(x):
    n=x/6+1
    return str(int(round(n))) if abs(n-round(n))<1e-3 else f'{x:.2f}'
def rw(y):
    for k,v in ROWS.items():
        if abs(y-k)<1e-3: return v
    return f'{y:.2f}'
def P(i): return nodes[i-1]
o=open('groups.txt','w',encoding='utf-8')
for s in range(len(NAMES)):
    idx=[k for k in range(N) if stf[k]==s]
    if not idx: continue
    o.write(f'\n#### {s+1}. {NAMES[s]}  n={len(idx)}\n')
    desc=collections.Counter()
    for k in idx:
        t,ns=els[k]
        if t==2: 
            zs=set(round(P(i)[2],2) for i in ns); desc[f'plate z={sorted(zs)}']+=1; continue
        a,b=P(ns[0]),P(ns[1])
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3:
            desc[f'V ax{ax(a[0])}/{rw(a[1])}']+=0  # placeholder
            desc[f'V {rw(a[1])}']+=1
        elif abs(a[1]-b[1])<1e-3:
            desc[f'X-dir row {rw(a[1])} z={round(a[2],2)}..{round(b[2],2)}']+=1
        elif abs(a[0]-b[0])<1e-3:
            desc[f'Y-dir ax {ax(a[0])} z={round(min(a[2],b[2]),1)}-{round(max(a[2],b[2]),1)}']+=1
        else:
            desc[f'diag z={round(a[2],2)}/{round(b[2],2)}']+=1
    for k,v in sorted(desc.items()):
        if v: o.write(f'   {v:4d}  {k}\n')
