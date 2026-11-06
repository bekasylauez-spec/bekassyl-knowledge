import re, json, collections
T=r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Data\galx.txt'
s=open(T,encoding='utf-8-sig').read()
def doc(n):
    m=re.search(r'\(\s*%d/(.*?)\n\s*\)'%n, s, re.S); return m.group(1)
els=[r.split() for r in doc(1).split('/') if r.strip()]
xyz=[list(map(float,r.split()[:3])) for r in doc(4).split('/') if r.strip() and len(r.split())>=3]
B=[]
for i,e in enumerate(els,1):
    if len(e)>=4 and e[1]=='8':
        a,b=int(e[2])-1,int(e[3])-1; B.append((i,xyz[a],xyz[b]))
print(len(B), len(xyz))
zs=collections.Counter(round(p[2],3) for _,p,q in B); print(zs)
json.dump(B,open('py/beams.json','w'))
# group by z, y-row or x-axis
for z in sorted(zs):
    rows=collections.defaultdict(list)
    for i,p,q in B:
        if round(p[2],3)!=z: continue
        if abs(p[1]-q[1])<1e-3: rows[('y',round(p[1],3))].append((min(p[0],q[0]),max(p[0],q[0])))
        else: rows[('x',round(p[0],3))].append((min(p[1],q[1]),max(p[1],q[1])))
    for k,v in sorted(rows.items()):
        v.sort(); print(z,k,len(v),round(v[0][0],3),round(v[-1][1],3))
