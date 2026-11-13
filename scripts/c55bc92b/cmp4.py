A=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/"
def f(x):
    x=x.replace(',','.')
    try: return float(x)
    except: return None
base={}
for l in open(A+"model_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); base[c[2]]=[f(x) for x in c[5:17]]
cur={}
for l in open("cur_dump_now.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); cur[c[2]]=[f(x) for x in c[3:15]]
n=0; mx=0; ncol=0
for k,c in cur.items():
    b=base[k]
    idx=range(12)
    if c[3] is None: idx=[0,1,2]+list(range(6,12)); ncol+=1
    m=max(abs(b[i]-c[i]) for i in idx); mx=max(mx,m)
    if m>0.05: n+=1; print("DIFF",k,m)
print("elements",len(cur),"columns(point)",ncol,"moved",n,"max dev mm",mx)
