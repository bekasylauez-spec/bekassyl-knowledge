import io,json,os,re
TASK=u"Порталы Блок 2-3 Карниз v3"
W=u"C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/%s.DOCS/AUTORES"%TASK
J=json.load(io.open(u"D:/РАБОЧКА/От Рас груп/3602 NRG Maftun Makon - Порталы/Расчет/"+TASK+".json",encoding='utf-8'))
nodes=J['nodes'];parts=J['parts']
pn=lambda n: next(p["name"] for p in parts if p["node_from"]<=n<=p["node_to"])
raw=open(os.path.join(W,'tbl09.23_1.csv'),'rb').read()
try: s=raw.decode('utf-8')
except: s=raw.decode('cp1251')
best={}
for l in s.splitlines()[1:]:
    r=l.split(';')
    if len(r)<8 or '(IV)' not in r[2]: continue
    try: n=int(r[4]); v=max(abs(float(r[5])),abs(float(r[6])))
    except: continue
    p=pn(n)
    if v>best.get(p,(0,))[0]: best[p]=(v,n,nodes[n-1])
print(best)
print([{k:v for k,v in p.items()} for p in parts])
import collections
col=[i+1 for i,c in enumerate(nodes) if abs(c[0]+385)<1 and abs(c[1]-25832)<1]
print('column nodes', [(n,nodes[n-1][2]) for n in col])
rows=collections.defaultdict(dict)
for l in s.splitlines()[1:]:
    r=l.split(';')
    if len(r)<8 or '(IV)' not in r[2]: continue
    try: n=int(r[4])
    except: continue
    if n in col: rows[(r[2],r[3])][n]=(float(r[5]),float(r[6]))
top=1129
for k,d in list(rows.items())[:40]:
    if top in d:
        z=sorted(col,key=lambda n:nodes[n-1][2])
        print(k, ['%d:%.1f/%.1f'%(nodes[n-1][2],*d[n]) for n in z if n in d][-6:])
