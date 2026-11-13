import sys
A=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/"
def f(x):
    x=x.replace(',','.'); 
    try: return float(x)
    except: return None
base={}
for l in open(A+"model_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); base[c[2]]=[f(x) for x in c[5:17]]
cur={}
for l in open("cur_dump_now.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); cur[c[2]]=[f(x) for x in c[3:15]]
print(len(base),len(cur),set(base)^set(cur))
n=0; mx=0
for k,c in cur.items():
    b=list(base[k]); c=list(c)
    if len(sys.argv)>1: b=b[:3]+[None]*3+b[6:]; c=c[:3]+[None]*3+c[6:]
    d=[(0 if x is None else x)-(0 if y is None else y) for x,y in zip(b,c)]
    m=max(abs(v) for v in d); mx=max(mx,m)
    if m>0.05: n+=1; print("DIFF",k,round(m,3),[round(v,2) for v in d])
print("diff elements",n,"max",mx)
