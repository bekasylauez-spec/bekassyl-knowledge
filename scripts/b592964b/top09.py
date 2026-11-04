import io,re,os,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
D=r"C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work\БЦ Лестница 02.DOCS\AUTORES"
t=io.open("БЦ Лестница 02.txt",encoding='utf-8-sig').read()
d1=t[t.index("( 1/"):t.index(")",t.index("( 1/"))]
E=[tuple(map(int,m)) for m in re.findall(r"(\d+) (\d+) (\d+) (\d+) /",d1)]
d4=t[t.index("( 4/"):t.index(")",t.index("( 4/"))]
N=[tuple(map(float,m)) for m in re.findall(r"([-\d.]+) ([-\d.]+) ([-\d.]+) /",d4)]
def rd(n):
    b=open(os.path.join(D,n),'rb').read()
    try:s=b.decode('utf-8-sig')
    except UnicodeDecodeError:s=b.decode('cp1251',errors='replace')
    L=s.splitlines();return L[0].split(';'),[r.split(';') for r in L[1:]]
best={}
for k in (1,2,3):
    h,R=rd('tbl15.49_%d.csv'%k);ie=h.index('ЭЛЕМЕНТ')
    pc=[i for i,c in enumerate(h) if c.endswith('%') and c!='М.У. %']
    for r in R:
        if len(r)<len(h)-1 or not r[ie].isdigit():continue
        e=int(r[ie])
        for i in pc:
            try:v=float(r[i])
            except:continue
            if v>best.get(e,(0,))[0]:best[e]=(v,h[i])
top=sorted(best.items(),key=lambda x:-x[1][0])[:12]
for e,(v,c) in top:
    typ,st,a,b=E[e-1];print(e,'st',st,round(v,1),c,N[a-1],N[b-1])
print('>100%:',sum(1 for v in best.values() if v[0]>100))
h,R=rd('tbl03.5_1.csv')
iz=h.index('ЗАГР');iu=h.index('УЗЕЛ')
S=collections.defaultdict(lambda:[0,0,0]);U=collections.defaultdict(dict)
for r in R:
    if len(r)<len(h)-1:continue
    try:z=int(r[1]);u=int(r[iu])
    except:continue
    ux,uy,uz=(float(r[h.index(k)]) for k in ('X','Y','Z'))
    U[z][u]=(ux,uy,uz)
    if z in (1,2,3):
        for j,v in enumerate((ux,uy,uz)):S[u][j]+=v
u=min(S,key=lambda u:S[u][2]);print('UZ 1+2+3 min',round(S[u][2],2),u,N[u-1])
for z in (5,6,7,8):
    if z in U:
        for j,n in ((0,'UX'),(1,'UY')):
            u=max(U[z],key=lambda u:abs(U[z][u][j]));print('load',z,n,round(U[z][u][j],2),N[u-1])
