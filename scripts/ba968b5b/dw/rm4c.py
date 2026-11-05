import ab, json, sys, re, km2_sec as K
sys.stdout.reconfigure(encoding='utf-8')
m=json.load(open('w/map6.json'))
print(ab.run([{'t':'erase','h':list(m['6.4'].values())+['3DA010']},{'t':'maprst'}],'er',300)[-150:])
print('stray', len(K.listwin([1000000,-1760000,1200000,-1700000])))
X0,Y0,X1,Y1=-456453.1,-1749172.3,-426753.1,-1728172.3
E=json.load(open('w/l62.json',encoding='utf-8'))
hs=[e['h'] for e in E if X0<=(e['e'][0]+e['e'][2])/2<=X1 and Y0<=(e['e'][1]+e['e'][3])/2<=Y1]
r=ab.run([{'t':'clonexf','hs':hs,'d':[789900.0,0]}],'cl4',600)
mm=re.search(r'clonexf\s+(.*)',r); m['6.4']=dict(p.split('>') for p in mm.group(1).split())
json.dump(m,open('w/map6.json','w'))
print(list(m['6.4'].items())[:2], len(K.listwin([333446.9,-1749172.3,363146.9,-1728172.3])))
