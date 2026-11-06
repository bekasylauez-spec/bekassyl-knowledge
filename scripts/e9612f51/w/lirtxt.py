import re, collections, json
t=open(r"C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Data\бдм блок 3 униф.txt",encoding='cp1251',errors='replace').read()
def doc(n):
    m=re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S); return m.group(1)
recs=lambda s:[r.split() for r in s.split('/') if r.strip()]
X=[list(map(float,r[:3])) for r in recs(doc(4))]
E=[list(map(int,r)) for r in recs(doc(1))]
st={}
for r in recs(doc(3)):
    if r[0]=='0' and r[1]=='S8': st[cur]=(float(r[3]),float(r[4]))
    elif r[0]!='0': cur=int(r[0])
beams=[]
for i,e in enumerate(E,1):
    ft,ty=e[0],e[1]; nd=e[2:]
    if ft in (2,10) and len(nd)==2:
        a,b=X[nd[0]-1],X[nd[1]-1]
        if abs(a[2]-b[2])<1e-3 and ty in st:
            beams.append(dict(el=i,st=ty,sec=st[ty],a=a,b=b))
c=collections.Counter((round(b['a'][2],3),b['sec']) for b in beams)
for k,v in sorted(c.items()): print(k,v)
json.dump(beams,open('beams.json','w'))
print(len(E),len(X),len(beams))
