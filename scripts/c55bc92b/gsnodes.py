import collections
F=[150]+[6000*i for i in range(1,10)]+[59850]
Y=[0,6000,12000,18000,24000,30000,36000]
def snap(v,arr): return min(arr,key=lambda a:abs(a-v))
nodes=collections.defaultdict(list)
for ln in open(r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\members.tsv',encoding='utf-8'):
    c=ln.rstrip('\n').split('\t')
    if c[1] not in ('ГС1','ГС2','Р3'): continue
    p=(float(c[4]),float(c[5])); q=(float(c[7]),float(c[8]))
    a=(snap(p[0],F),snap(p[1],Y)); b=(snap(q[0],F),snap(q[1],Y))
    for n,o in ((a,b),(b,a)):
        d=('+x' if o[0]>n[0] else '-x')+('' if o[1]==n[1] else ('+y' if o[1]>n[1] else '-y'))
        nodes[n].append(c[1]+d)
cnt=collections.Counter()
for n in sorted(nodes):
    k=' '.join(sorted(nodes[n])); cnt[(n[1],k)]+=1
for (y,k),v in sorted(cnt.items()): print(y, v, k)
