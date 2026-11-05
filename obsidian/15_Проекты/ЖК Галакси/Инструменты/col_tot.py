import csv,pickle,collections,sys,math
sys.path.insert(0,'.'); import model as M
els,nodes=pickle.load(open('lira6/m.pkl','rb'))
R=collections.defaultdict(list)
for r in csv.reader(open('arm/as_bar.csv',encoding='utf-8',errors='replace'),delimiter=';'):
    if len(r)<20 or not r[4].strip().isdigit(): continue
    g=int(r[2])
    if g not in (5,6,17,18): continue
    try: v=[float(x) for x in r[10:18]]
    except: continue
    if r[6].strip('﻿')=='*': continue
    R[int(r[4])].append(v)
cols=collections.defaultdict(list)
for e,rows in R.items():
    ns=[nodes[int(k)-1] for k in els[e-1][2:4]]
    x=round(ns[0][0]*1000); y=round(M.fy(ns[0][1])); z0=min(n[2] for n in ns)
    tot=max(sum(v) for v in rows); au=max(max(v[:4]) for v in rows); asf=max(max(v[4:]) for v in rows)
    cols[(x,y)].append((z0,tot,au,asf))
A={d:math.pi*d*d/400 for d in (16,18,20,22,25,28,32)}
G=max(t for k in cols for z,t,a,s in cols[k])
for k in sorted(cols):
    mx=max(t for z,t,a,s in cols[k])
    print(k, ' '.join('z%.2f tot%.2f au%.2f as%.2f'%r for r in sorted(cols[k])), '| max', round(mx,2))
print('GLOBAL max', round(G,2))
for n in (8,12,16):
    need=G/n; d=min(d for d in A if A[d]>=need) if any(A[d]>=need for d in A) else None
    print(n,'bars: need %.2f per bar ->'%need, d, 'Ø', round(A[d],2) if d else '')
