import json,collections
R=json.load(open('../an/rects.json'))
LV={'1':-0.05,'2':4.5,'3':7.0}
out=[]
for k,z in LV.items():
    B=R[k]['beam']
    groups=collections.defaultdict(list)
    for x0,y0,x1,y1 in B:
        w,h=x1-x0,y1-y0
        if w>=h: groups[('X',(y0+y1)/2,h)].append((x0,x1))
        else: groups[('Y',(x0+x1)/2,w)].append((y0,y1))
    for (d,c,b),segs in sorted(groups.items()):
        segs.sort()
        # split into chains where gap > 1300
        ch=[[segs[0]]]
        for s in segs[1:]:
            if s[0]-ch[-1][-1][1]>1300: ch.append([s])
            else: ch[-1].append(s)
        for c2 in ch:
            out.append(dict(z=z,d=d,c=c,b=b,segs=c2))
            print(z,d,c,b,len(c2),c2[0][0],c2[-1][1],[s[1]-s[0] for s in c2])
json.dump(out,open('lines.json','w'))
print(len(out))
