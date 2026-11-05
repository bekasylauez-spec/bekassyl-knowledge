import csv,pickle,collections,sys
sys.path.insert(0,'.'); import model as M
els,nodes=pickle.load(open('lira6/m.pkl','rb'))
R=collections.defaultdict(list); grp={}
for r in csv.reader(open('arm/as_bar.csv',encoding='utf-8',errors='replace'),delimiter=';'):
    if len(r)<20 or not r[4].strip().isdigit(): continue
    g=int(r[2]); 
    if g not in (5,6,17,18): continue
    e=int(r[4]); sec=int(r[5])
    try: v=[float(x) for x in r[10:22]]
    except: continue
    R[e].append((sec,r[6].strip('﻿'),v))
cols=collections.defaultdict(list)
for e,rows in R.items():
    ns=[nodes[int(k)-1] for k in els[e-1][2:4]]
    x=ns[0][0]*1000; y=M.fy(ns[0][1]); z0=min(n[2] for n in ns); z1=max(n[2] for n in ns)
    au=max(max(v[0:4]) for s,t,v in rows if t!='*'); As=max(max(v[4:8]) for s,t,v in rows if t!='*')
    asw=max(max(v[9:11]) for s,t,v in rows if t!='*')
    cols[(round(x),round(y))].append((z0,z1,au,As,asw,max(v[8] for s,t,v in rows)))
for k in sorted(cols):
    print(k)
    for z0,z1,au,As,asw,mu in sorted(cols[k]): print('   %6.2f..%6.2f AUmax %.2f ASmax %.2f ASW %.2f mu %.2f'%(z0,z1,au,As,asw,mu))
