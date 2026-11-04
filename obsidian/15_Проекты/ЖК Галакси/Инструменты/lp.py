import re, sys, collections, pickle
txt=open(sys.argv[1],'rb').read().decode('cp1251',errors='replace')
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\n\s*\)', txt, re.S):
    docs.setdefault(int(m.group(1)), m.group(2))
def recs(s): return [r.split() for r in s.replace('\n',' ').split('/') if r.strip()]
els=[r for r in recs(docs[1])]
nodes=[tuple(map(float,r[:3])) for r in recs(docs[4])]
print('elements',len(els),'nodes',len(nodes))
c=collections.Counter((r[0],r[1]) for r in els); print(c.most_common(40))
zs=collections.Counter(round(n[2],3) for n in nodes); print(sorted(zs.items()))
xs=sorted(set(round(n[0],3) for n in nodes)); ys=sorted(set(round(n[1],3) for n in nodes))
print('x',xs[0],xs[-1],len(xs),'y',ys[0],ys[-1],len(ys))
pickle.dump((els,nodes),open(sys.argv[2],'wb'))
