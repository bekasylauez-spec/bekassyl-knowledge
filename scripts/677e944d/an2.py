import sys, collections, math
sys.argv=['x']
exec(open('an_nodes.py',encoding='utf-8').read().split('print("=== БОЛТТАР')[0])
def cen(p): 
    V=p['V']; return tuple(round(sum(v[i] for v in V)/len(V)) for i in range(3))
def who(p):
    c=collections.Counter()
    for k,v in p['edge'].items():
        if k!='-': c['қыр:'+cls(k)]+=round(v)
    for k,v in p['fa'].items(): c['бетА:'+cls(k)]+=int(v)
    for k,v in p['fb'].items(): c['бетБ:'+cls(k)]+=int(v)
    return dict(c)
want={('узел 7',405,236),('узел 7',300,64),('узел 7',300,57),('узел 8',220,200),('узел 9',232,50),('узел 9',232,40),('узел 9',200,200),('узел 9',130,100),('узел 7',523,188),('узел 7',525,188),('узел 7',268,188),('узел 7',268,268),('узел 7',270,268),('узел 5',256,253),('узел 5',453,253),('узел 6',526,218),('узел 4',348,338),('узел 2',620,220)}
grp=collections.defaultdict(list)
for i,p in plates.items():
    a,b=dims(p); k=(p['key'],max(a,b),min(a,b))
    if k in want: grp[k].append(i)
for k in sorted(grp):
    sig=collections.Counter()
    for i in grp[k]:
        w=who(plates[i]); sig[tuple(sorted(w))]+=1
    print(k,len(grp[k]))
    for s,c in sig.most_common(4):
        ex=[i for i in grp[k] if tuple(sorted(who(plates[i])))==s][0]
        print('   ',c,'×',who(plates[ex]),'| мыс. орны',cen(plates[ex]),'per',round(plates[ex]['per']),'tot',plates[ex]['tot'])
# bolts of node 9 odd, node 11
print('--- узел 9 тақ болттар')
for b in bolts:
    if b['key']=='узел 9' and len(b['p'])<3: print('  Ø%d'%round(b['d']),[round(v) for v in b['a']],{cls(k):v for k,v in b['p'].items()})
