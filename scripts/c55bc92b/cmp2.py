A=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/"
def num(x):
    try:return float(x.replace(',','.'))
    except:return None
base={};cur={}
for l in open(A+"model_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); base[c[2]]=c
for l in open("cur_dump.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); cur[c[2]]=c
n=0
for k,c in cur.items():
    b=base[k]
    bp=b[5:8]+b[11:17]; cp=c[3:6]+c[9:15]
    d=[(num(x) or 0)-(num(y) or 0) for x,y in zip(bp,cp)]
    if max(abs(v) for v in d)>0.5: n+=1; print("MOVED",k,"was",bp,"now",cp)
print("moved vs 15:07 dump",n)
mem={}
for l in open(A+"members.tsv",encoding='utf-8'):
    c=l.rstrip('\n').split('\t'); mem[c[1]+"-"+c[0]]=c
off=0;cmpd=0
for k,m in mem.items():
    c=cur[k]; p=[float(x) for x in m[4:7]]; q=[float(x) for x in m[7:10]]
    cp=[num(x) for x in c[3:6]]
    if m[3]=='col':
        cmpd+=1
        if abs(cp[0]-p[0])>1 or abs(cp[1]-p[1])>1: off+=1; print("COL OFF",k,"nominal",p,"model",cp)
print("col compared",cmpd,"off",off)
# beams: count whose location endpoints match nominal p/q either order
ok=nok=0
for k,m in mem.items():
    if m[3]=='col': continue
    c=cur[k]; p=[float(x) for x in m[4:7]]; q=[float(x) for x in m[7:10]]
    a=[num(x) for x in c[3:6]]; b=[num(x) for x in c[6:9]]
    if None in a or None in b: nok+=1; continue
    d1=max(abs(x-y) for x,y in zip(p+q,a+b)); d2=max(abs(x-y) for x,y in zip(p+q,b+a))
    if min(d1,d2)<=1: ok+=1
    else: nok+=1
print("non-col match nominal",ok,"no-match",nok)
