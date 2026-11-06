import json, collections
bars=json.load(open('bars.json'))
SEC={'20':'25x60','22':'50x70','23':'35x70','24':'50x90','25':'50x90','26':'50x90','27':'60x100','28':'60x120','44':'50x70','45':'60x70'}
lines=collections.defaultdict(list)
for k,s in SEC.items():
    for i,a,b in bars[k]:
        z=round(a[2],3)
        if k=='44' and z!=7.0: continue
        if abs(a[1]-b[1])<1e-3: key=(z,'X',round(a[1],3)); r=sorted([a[0],b[0]])
        elif abs(a[0]-b[0])<1e-3: key=(z,'Y',round(a[0],3)); r=sorted([a[1],b[1]])
        else: key=(z,'D',0); r=[0,0]
        lines[key].append((r[0],r[1],s))
for key in sorted(lines):
    segs=sorted(lines[key]); runs=[]
    for a,b,s in segs:
        if runs and abs(runs[-1][1]-a)<1e-3 and runs[-1][2]==s: runs[-1][1]=b
        else: runs.append([a,b,s])
    print(key, [(round(a,3),round(b,3),s) for a,b,s in runs])
