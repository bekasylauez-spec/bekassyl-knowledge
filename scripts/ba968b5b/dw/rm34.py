import ab, json, sys, km2_sec as K, os, re
sys.stdout.reconfigure(encoding='utf-8')
X0,Y0,X1,Y1=-456453.1,-1749172.3,-426753.1,-1728172.3
print('free', len(K.listwin([303747.5,-1749172,363147,-1728172])))
E=json.load(open('w/l62.json',encoding='utf-8'))
hs=[e['h'] for e in E if X0<=(e['e'][0]+e['e'][2])/2<=X1 and Y0<=(e['e'][1]+e['e'][3])/2<=Y1]
print(len(hs))
out={}
for name,dx in (('6.3',760200.0),('6.4',789900.0)):
    r=ab.run([{'t':'clonexf','hs':hs,'d':[dx,0],'pre':''}],'cl'+name,600)
    m=re.search(r'clonexf\s+(.*)',r)
    out[name]=dict(p.split('>') for p in m.group(1).split())
    print(name,len(out[name]))
json.dump(out,open('w/map6.json','w'))
print(ab.run([{'t':'layouts'}],'lay',100)[-600:])
