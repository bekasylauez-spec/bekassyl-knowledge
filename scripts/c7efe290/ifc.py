import sys,io
sys.stdout=io.TextIOWrapper(open(r'D:/_claude_work/v113/src/ifc_out.txt','wb'),encoding='utf-8')
#113\src\ifc_out.txt','wb'),encoding='utf-8')
import re,collections
t=open('km.ifc',encoding='cp1251',errors='replace').read()
def dec(s):
    return re.sub(r'\\X2\\([0-9A-F]+)\\X0\\',lambda m:''.join(chr(int(m.group(1)[i:i+4],16)) for i in range(0,len(m.group(1)),4)),s)
ent={}
for m in re.finditer(r'^#(\d+)= *(\w+)\((.*)\);\s*$',t,re.M):
    ent[int(m.group(1))]=(m.group(2),dec(m.group(3)))
print(len(ent))
# assemblies
asm={}
for i,(k,a) in ent.items():
    if k=='IFCELEMENTASSEMBLY':
        asm[i]=re.search(r"'([^']*)',\.NOTDEFINED\.",a).group(1)
print(collections.Counter(asm.values()).most_common(40))
parent={}
for i,(k,a) in ent.items():
    if k=='IFCRELAGGREGATES':
        m=re.match(r"'[^']*',#\d+,\$,\$,#(\d+),\(([^)]*)\)",a)
        if m:
            for c in re.findall(r'#(\d+)',m.group(2)): parent[int(c)]=int(m.group(1))
# placement abs
def pt(i):
    return [float(x) for x in re.findall(r'-?[\d.]+(?:E[-+]?\d+)?',ent[i][1])]
def a2p(i):
    m=re.match(r'(#\d+|\$),?(#\d+|\$)?,?(#\d+|\$)?',ent[i][1])
    a=ent[i][1]
    ids=re.findall(r'#(\d+)|\$',a)
    refs=re.findall(r'(#\d+|\$)',a)
    return refs
import math
def lp(i,depth=0):
    a=ent[i][1]
    refs=re.findall(r'(#\d+|\$)',a)
    rel=None if refs[0]=='$' else int(refs[0][1:])
    ax=int(refs[1][1:])
    r=re.findall(r'(#\d+|\$)',ent[ax][1])
    loc=pt(int(r[0][1:]))
    z=pt(int(r[1][1:])) if r[1]!='$' else [0,0,1]
    x=pt(int(r[2][1:])) if len(r)>2 and r[2]!='$' else [1,0,0]
    return rel,loc,z,x
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def absloc(i):
    rel,loc,z,x=lp(i)
    if rel is None:return loc
    pl=absmat(rel)
    return apply(pl,loc)
def absmat(i):
    rel,loc,z,x=lp(i)
    y=cross(z,x)
    M=(loc,x,y,z)
    if rel is None:return M
    P=absmat(rel)
    o=apply(P,loc)
    return (o,[sum(P[1][k]*x[0]+P[2][k]*x[1]+P[3][k]*x[2] for _ in [0]) for k in range(3)],[P[1][k]*y[0]+P[2][k]*y[1]+P[3][k]*y[2] for k in range(3)],[P[1][k]*z[0]+P[2][k]*z[1]+P[3][k]*z[2] for k in range(3)])
def apply(M,v):
    return [M[0][k]+M[1][k]*v[0]+M[2][k]*v[1]+M[3][k]*v[2] for k in range(3)]
rows=[]
for i,(k,a) in ent.items():
    if k in('IFCCOLUMN','IFCBEAM','IFCMEMBER','IFCPLATE'):
        p=re.match(r"'[^']*',#\d+,'([^']*)','([^']*)','([^']*)',#(\d+),#(\d+)",a)
        name=p.group(1); pl=int(p.group(4)); pds=int(p.group(5))
        # depth
        sh=ent[pds][1]; reps=re.findall(r'#(\d+)',sh)
        depth=None
        for r in reps:
            if ent[int(r)][0]=='IFCSHAPEREPRESENTATION':
                for it in re.findall(r'#(\d+)',ent[int(r)][1]):
                    e=ent[int(it)]
                    if e[0]=='IFCEXTRUDEDAREASOLID':
                        depth=float(e[1].split(',')[-1])
        try:
            o=absloc(pl)
        except Exception as ex:
            o=None
        rows.append((i,k,name,asm.get(parent.get(i),None),o,depth))
import json
json.dump(rows,open('rows.json','w'),ensure_ascii=False)
for key in ['IFCCOLUMN','IFCBEAM','IFCMEMBER']:
    c=collections.Counter((r[2],r[3]) for r in rows if r[1]==key)
    print(key);[print('  ',v,kk) for kk,v in sorted(c.items())]
for r in rows[:5]:print(r)
print('=====SUMMARY')
g=collections.defaultdict(list)
for r in rows:
    if r[1]!='IFCPLATE': g[(r[1],r[2],r[3])].append(r)
for k,v in g.items():
    pass
# profile names per element
prof={}
for i,(k,a) in ent.items():
    if k in('IFCCOLUMN','IFCBEAM','IFCMEMBER'):
        prof[i]=re.match(r"'[^']*',#\d+,'[^']*','([^']*)'",a).group(1)
g=collections.defaultdict(list)
for r in rows:
    if r[1]!='IFCPLATE': g[(r[1],prof[r[0]],r[3])].append(r)
for k,v in sorted(g.items()):
    xs=[r[4][0] for r in v];ys=[r[4][1] for r in v];zs=[r[4][2] for r in v];ds=sorted(set(round(r[5] or 0) for r in v))
    print(k,len(v),'X',round(min(xs)),round(max(xs)),'Y',round(min(ys)),round(max(ys)),'Z',round(min(zs)),round(max(zs)),'depths',ds[:12])
pc=collections.Counter()
for r in rows:
    if r[1]=='IFCPLATE':
        pc[ (re.search(r"'[^']*',#\d+,'[^']*','([^']*)'",ent[r[0]][1]).group(1), r[3]) ]+=1
for k,v in sorted(pc.items()):print('PLATE',k,v)
for i,(k,a) in ent.items():
    if k=='IFCGRID' or k=='IFCGRIDAXIS' and False: print(k,a[:200])
for i in (4492,4496,4528,4532,4536,4540):
    print(i,ent[i])
