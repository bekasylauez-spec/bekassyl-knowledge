# LIRA «Навес 1 Рампа 02» -> model.txt for the Revit builder (mm, Revit X/Y = LIRA X/Y: Л at Y=0, М at 7300, К2 row at 8800 as on the КМ plans; Z = LIRA z + 870)
import re, collections
t=open(r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Data\Навес 1 Рампа 02.txt',encoding='utf-8-sig').read()
def doc(n):
    i=t.find('( %d/'%n); j=t.find(')',i); return t[i+len('( %d/'%n):j]
N=[tuple(map(float,r.split())) for r in doc(4).split('/') if r.strip()]
E=[tuple(map(int,r.split())) for r in doc(1).split('/') if r.strip()]
Z0=870.0
P=lambda n:(N[n-1][0]*1000, N[n-1][1]*1000, N[n-1][2]*1000+Z0)
FAM={1:'Труба 140x100x4',2:'Труба 80x3',3:'Труба 80x3',4:'Труба 50x2.5',5:'Труба 60x2.5',6:'Труба 50x2.5',7:'Труба 50x2.5',8:'Труба 50x2.5'}
PROF={'Труба 140x100x4':(100,140,4),'Труба 80x3':(80,80,3),'Труба 60x2.5':(60,60,2.5),'Труба 50x2.5':(50,50,2.5)}
chord=[e for e in E if e[0]==10 and e[1]==3]
cn=set(n for e in chord for n in e[2:])
def is_bottom(n):
    x,y,z=N[n-1]
    return any(abs(N[m-1][0]-x)<1e-3 and abs(N[m-1][1]-y)<1e-3 and N[m-1][2]>z+0.05 for m in cn if m!=n)
out=[]
for nm,v in PROF.items(): out.append('F|%s|%g|%g|%g'%(nm,v[0],v[1],v[2]))
for nm,x in (('1',0),('2',5800),('3',11800),('3/1',16200),('4',17800),('5',20800)):
    out.append('G|%s|%g|%g|%g|%g'%(nm,x,-2600,x,10600))
for nm,y in (('Л',0),('М',7300)):
    out.append('G|%s|%g|%g|%g|%g'%(nm,-2600,y,26600,y))
cnt=collections.Counter()
for k,(typ,st,a,b) in enumerate(E,1):
    pa,pb=P(a),P(b)
    vert=abs(pa[0]-pb[0])<1 and abs(pa[1]-pb[1])<1
    if vert and st in (1,2):
        lo,hi=(pa,pb) if pa[2]<pb[2] else (pb,pa)
        out.append('C|%s|%s|%.1f|%.1f|%.1f|%.1f|%d'%(FAM[st],'К1' if st==1 else 'К2',lo[0],lo[1],lo[2],hi[2],k)); cnt['col '+str(st)]+=1
        continue
    if st==1: mk='К1'
    elif st==2: mk='Пк1'
    elif st==3: mk='НП1' if (is_bottom(a) and is_bottom(b)) else 'ВП1'
    elif st==7: mk='СВ2' if abs(N[a-1][1])<1e-3 else 'СВ1'   # Л row = СВ2, М row = СВ1 (sheet 4)
    elif st==8 and abs(N[a-1][2]-N[b-1][2])>0.05: mk='СВ3'   # V braces between trusses (sections 3-3, 4-4)
    else: mk={4:'Р1',5:'П1',6:'СГ1',8:'РС1'}[st]
    zj='B' if mk=='П1' else 'C'
    out.append('B|%s|%s|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%s|%d'%(FAM[st],mk,*pa,*pb,zj,k)); cnt[mk]+=1
# columns merged: K1 consists of 3 bars (21-22,22-13,13-1) on one vertical -> merge collinear verticals
cols=[o for o in out if o.startswith('C|')]; rest=[o for o in out if not o.startswith('C|')]
grp=collections.defaultdict(list)
for c in cols:
    f=c.split('|'); grp[(f[1],f[2],f[3],f[4])].append((float(f[5]),float(f[6]),f[7]))
mc=[]
for (fa,mk,x,y),segs in grp.items():
    segs.sort(); z1=segs[0][0]; z2=max(s[1] for s in segs)
    mc.append('C|%s|%s|%s|%s|%.1f|%.1f|%s'%(fa,mk,x,y,z1,z2,'+'.join(s[2] for s in segs)))
# embedded plates (КЖ): Зд-1 -18 250x280 under К1, Зд-2 -12 180x180 under К2
pl=[]
for c in mc:
    f=c.split('|')
    if f[2]=='К1': pl.append('D|Зд-1|%s|%s|%g|250|280|18'%(f[3],f[4],Z0))
    else: pl.append('D|Зд-2|%s|%s|%g|180|180|12'%(f[3],f[4],Z0))
open('model.txt','w',encoding='utf-8').write('\n'.join(rest+mc+pl)+'\n')
print(len(N),'nodes',len(E),'bars',cnt, len(mc),'columns', collections.Counter(c.split('|')[2] for c in mc))
for c in mc[:6]: print(c)
