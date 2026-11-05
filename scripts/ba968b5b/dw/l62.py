import km2_sec as K, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
E=K.listwin([-456453.1,-1749172.3,-426753.1,-1728172.3])
json.dump(E,open('w/l62.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(E), collections.Counter(e['t'] for e in E))
for e in E:
    x0,y0,x1,y1=e['e']
    if e['t'] in ('DIMENSION',) or (e['t'] in('LWPOLYLINE','LINE') and (x1-x0)>3000):
        print(e['t'],e['h'],e['lay'],[round(v) for v in e['e']],[tuple(round(c) for c in p) for p in e['pts'][:6]])
