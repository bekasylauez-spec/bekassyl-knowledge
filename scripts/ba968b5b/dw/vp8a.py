import ab, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
def ents(s):
    out=[]
    for l in open('w/ext_%s.txt'%s,encoding='utf-8-sig'):
        p=l.rstrip('\n').split('|')
        if len(p)<8 or not p[3]: continue
        out.append(dict(h=p[0],t=p[1],lay=p[2],e=tuple(map(float,p[3:7])),info=p[7]))
    return out
X0,Y0,X1,Y1=-661803.1,-1749172.3,-646953.1,-1728172.3
keep=[]
for e in ents('3.7'):
    cx=(e['e'][0]+e['e'][2])/2; cy=(e['e'][1]+e['e'][3])/2
    if not (X0<cx<X1 and Y0<cy<Y1): continue
    if e['t'] in ('SPDSFORMAT','ACAD_TABLE') or (cx>-657300 and cy<-1736000): keep.append((e['h'],e['t'],e['info'][:40]))
for k in keep: print(k)
D=363146.9-X0
ab.run([{'t':'maprst'}],'mr',60)
r=ab.run([{'t':'clonexf','hs':[k[0] for k in keep],'d':[D,0]}],'c38',300)
m=re.search(r'clonexf\s+(.*)',r); M=dict(p.split('>') for p in m.group(1).split())
json.dump(M,open('w/map38.json','w')); print(len(M))
