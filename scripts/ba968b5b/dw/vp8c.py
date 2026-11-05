import ab, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
exec(open('vp8a.py',encoding='utf-8').read().split('X0,Y0')[0])
M=json.load(open('w/map38.json'))
X38=364146.9; T1=-1737793.9
def band(s, x0, top, h=1000, x1=None):
    x1 = x1 or x0+3150
    return [e['h'] for e in ents(s) if x0-50<(e['e'][0]+e['e'][2])/2<x1 and top-h<(e['e'][1]+e['e'][3])/2<top]
def clone(hs, d, key):
    ab.run([{'t':'maprst'}],'mr',60)
    r=ab.run([{'t':'clonexf','hs':hs,'d':d}],'cv',300)
    m=re.search(r'clonexf\s+(.*)',r); M[key]=dict(p.split('>') for p in m.group(1).split()); print(key,len(hs),len(M[key]))
O42=260896.873; O43=290596.873; R1=-1729422.265
dy=T1-R1
clone(band('4.2',O42,-1728300,h=1122), [X38-O42, dy], 'vhdr')              # title + header
for src,(o,s) in ((1,(O42,'4.2')),(2,(O42,'4.2'))): clone(band(s,o,R1-(src-1)*1000), [X38-o, dy], 'v2_%d'%src)
clone(band('4.2',O42,R1-4000), [X38-O42, dy+2000], 'v2_5')
for src,slot in ((1,4),(2,5),(5,6)): clone(band('4.3',O43,R1-(src-1)*1000), [X38-O43, dy-(slot-src)*1000], 'v3_%d'%src)
O37=-660803.127; T37=-1737793.9
for k,src,slot in (('b3',5,7),('b4',6,8),('b5',5,9),('b6',6,10)):
    hs=band('3.7',O37,T37-(src-1)*1000)
    clone(hs, [X38-O37, (T37-(src-1)*1000)-(T1-(slot-1)*1000) and -((src-slot)*1000)], k)
for slot in (7,8,9,10): clone(['3D4E6C'], [X38-O42, (T1-(slot-1)*1000)-R1], 'fr%d'%slot)
json.dump(M,open('w/map38.json','w'))
