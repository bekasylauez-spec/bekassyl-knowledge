import sys,collections; sys.path.insert(0,sys.argv[1]); import csvread
g,r=csvread.load(sys.argv[2])
names=collections.Counter(v.split('/')[0].split('-',1)[1].strip() for v in g.values()); print(names)
for k,v in g.items():
  if 'олонн' in v or 'ва' in v.split('/')[0]:
    els=sorted({x['el'] for x in r if x['g']==k}); print(k,v[:75],len(els),els[:8])
