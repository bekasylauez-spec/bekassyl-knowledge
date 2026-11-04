import math,re
w={6:0.222,8:0.395,10:0.617,12:0.888,14:1.208,16:1.578,18:1.998,20:2.466,22:2.984,25:3.853,28:4.834,32:6.313}
rows=[]
for l in open(r"C:/Users/Admin/AppData/Local/Temp/claude/D---------/4ae264b2-3d49-4a11-8864-2d6523e82a02/scratchpad/dxf/f04.tables.txt",encoding='utf-8-sig'):
    if l.strip().startswith('TABLE 6A1337'): break
    m=re.match(r'\s+R(\d+) h=\S+ \| (.*)',l)
    if m and 'ГОСТ 34028' in l and '%%C' in l:
        c=[x.strip() for x in m.group(2).split('|')]
        num=lambda s: float(s.split()[0])
        d=int(c[3]); L=c[9]; n=num(c[10]); ue=num(c[11]); tot=num(c[12])
        rows.append((c[0],d,L,n,ue,tot))
by={}
s=0
for p,d,L,n,ue,tot in rows:
    if L=='пог.м.': calc=n*w[d]; 
    else: calc=float(L)/1000*w[d]*n
    flag='' if abs(calc-tot)<max(1,0.005*tot) else ' <<<'
    print(p,d,L,n,ue,tot,round(calc,2),flag)
from collections import defaultdict
S=defaultdict(float)
for p,d,L,n,ue,tot in rows:
    k=1032 if p in('55','56') else 1
    S[d]+=tot*k
print({k:round(v,2) for k,v in sorted(S.items())}, round(sum(S.values()),2))
