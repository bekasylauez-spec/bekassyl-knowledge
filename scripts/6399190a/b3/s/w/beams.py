import sys,json,collections; sys.path.insert(0,sys.argv[1]); import model
els,nodes,docs=model.load(sys.argv[2])
sec={15:(55,55),16:(70,70),17:(50,70),18:(130,90),19:(50,90),20:(50,115),21:(50,120),22:(50,145),23:(50,160),24:(75,170),36:(90,90)}
cols=json.load(open(sys.argv[3]))
nd_at=collections.defaultdict(list)
for i,e in enumerate(els):
    if e[0] in(10,5,2) and len(e)>=4:
        for n in e[2:4]: nd_at[n].append(i+1)
def key(p): return tuple(round(v,3) for v in p)
idx={key(p):i+1 for i,p in enumerate(nodes)}
pos=collections.defaultdict(set)
for g,lst in cols.items():
    for c in lst: pos[(round(c['a'][0],2),round(c['a'][1],2))].update([round(c['a'][2],2),round(c['b'][2],2)])
for (x,y),zs in sorted(pos.items(),key=lambda k:(k[0][1],k[0][0])):
    out=[]
    for z in sorted(zs):
        n=idx.get(key((x,y,z)))
        bs=[]
        for ei in nd_at.get(n,[]):
            t,st,a,b=els[ei-1][:4]
            pa,pb=nodes[a-1],nodes[b-1]
            if abs(pa[2]-pb[2])<0.01 and st in sec: bs.append(sec[st])
        if bs: out.append((z,sorted(set(bs))))
        else: out.append((z,'-'))
    print((x,y),out)
