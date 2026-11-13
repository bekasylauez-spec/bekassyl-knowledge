import sys
A=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/"
base={}
for l in open(A+"model_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); base[c[2]]=c
cur={}
for l in open("cur_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); cur[c[2]]=c
print(len(base),len(cur), set(base)-set(cur), set(cur)-set(base))
def num(x):
    try:return float(x)
    except:return None
n=0
for k,c in cur.items():
    b=base.get(k)
    if not b: continue
    # base: idx mk im type fam pa(3) pb(3) bbox(6) ...  ; cur: id mk im pa(3) pb(3) bbox(6)
    bp=b[5:11]+b[11:17]; cp=c[3:9]+c[9:15]
    d=[ (num(x) or 0)-(num(y) or 0) for x,y in zip(bp,cp)]
    if max(abs(v) for v in d)>0.5:
        n+=1; print("MOVED",k,c[1],"was",bp,"now",cp)
print("moved",n)
# members check for columns: members rows: id mark kind fam px py pz qx qy qz
mem={}
for l in open(A+"members.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); mem[c[1]+"-"+c[0]]=c
bad=0;miss=0
for k,m in mem.items():
    c=cur.get(k)
    if not c: miss+=1; print("no model inst",k); continue
    p=[float(x) for x in m[4:7]]; q=[float(x) for x in m[7:10]]
    if m[3]=='col': # LocationPoint at p
        cp=[float(c[3]),float(c[4])]
        if abs(cp[0]-p[0])>1 or abs(cp[1]-p[1])>1: bad+=1; print("COL OFF",k,"nominal",p[:2],"model",cp, "bbox",c[9:15])
print("members",len(mem),"missing",miss,"col offs",bad)
