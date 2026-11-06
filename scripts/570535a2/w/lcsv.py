import sys,re,collections
p=r"R:\От Маке\Завод\Маслоподготовка Блок 2\Расчет\csv\tbl01.31_1.csv"
raw=open(p,'rb').read().decode('utf-8','replace').replace('\ufeff','')
grp={};cur=None;stat=collections.defaultdict(lambda:{'els':set(),'tot':0,'au':0,'as':0,'row':None})
for ln in raw.splitlines():
    c=ln.split(';')
    if len(c)<3: continue
    if c[1].endswith('-S'): cur=c[1][:-2]; grp[cur]=c[2].strip(); continue
    if c[0]=='Id': continue
    if '*' in c[6]: continue
    try: v=[float(x) for x in c[10:18]]
    except: continue
    s=stat[c[1]]; s['els'].add(c[4]); t=sum(v)
    if t>s['tot']: s['tot']=t; s['row']=(c[4],c[5],v)
for g in sorted(grp,key=lambda x:int(x)):
    s=stat[g]; print(g,'|',grp[g][:110],'| n_el',len(s['els']),'| maxTot %.2f'%s['tot'],s['row'])
print('=====')
for g in sorted(grp,key=lambda x:int(x)):
    n=grp[g]; m=re.search(r'B=([\d.]+)/ H=([\d.]+).*?L=([\d.]+)',n)
    if not m or not re.match(r'\d+ - K',n): continue
    s=stat[g]; print(g,m.groups(),'n_el',len(s['els']),'maxTot %.2f'%s['tot'],s['row'], 'els',sorted(s['els'],key=int)[:40])
