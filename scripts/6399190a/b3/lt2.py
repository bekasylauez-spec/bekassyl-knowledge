import re,json,collections
T=open("D:/РАБОЧКА/От Маке/Завод/Маслоподготовка Блок 3/Расчет/массаподготовка блок 3 униф.txt",encoding='utf-8-sig').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)\s*/(.*?)\)',T,re.S): docs.setdefault(int(m.group(1)),m.group(2))
el=[list(map(int,r.split())) for r in docs[1].split('/') if r.strip()]
xyz=[list(map(float,r.split()[:3])) for r in docs[4].split('/') if r.strip()]
S0={}
for r in docs[3].split('/'):
    p=r.split()
    if len(p)>=5 and p[1] in('S0','S6'): S0[int(p[0])]=(p[1],float(p[3]),float(p[4]) if len(p)>4 else 0)
COL={14,15,18,19}
nodebars=collections.defaultdict(list)
for i,r in enumerate(el,1):
    if r[0]==10 and len(r)==4:
        for n in r[2:]: nodebars[n].append(i)
out={}
for i,r in enumerate(el,1):
    if r[0]==10 and r[1] in COL:
        a,b=r[2],r[3]
        for n in (a,b):
            z=xyz[n-1][2]; key=(round(xyz[n-1][0],2),round(xyz[n-1][1],2))
            hs=[]
            for j in nodebars[n]:
                rr=el[j-1]; p,q=xyz[rr[2]-1],xyz[rr[3]-1]
                if abs(p[2]-q[2])<1e-3:
                    s=S0.get(rr[1]); hs.append((rr[1],s[1:] if s else None))
            out.setdefault(str(key),{})[round(z,3)]=sorted(set(hs))
print('beam stiff:',{k:v for k,v in S0.items()})
for k in sorted(out,key=lambda s:(eval(s)[1],eval(s)[0])):
    print(k, {z:v for z,v in sorted(out[k].items())})
