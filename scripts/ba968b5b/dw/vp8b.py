import ab, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
exec(open('vp8a.py',encoding='utf-8').read().split('X0,Y0')[0])
M=json.load(open('w/map38.json'))
for s,w,dx,key in (('4.2',(250900,-1734300,255850,-1729000),113227.0,'s2'),('4.3',(280000,-1735000,290400,-1729000),87590.0,'s3')):
    hs=[e['h'] for e in ents(s) if w[0]<(e['e'][0]+e['e'][2])/2<w[2] and w[1]<(e['e'][1]+e['e'][3])/2<w[3]]
    ab.run([{'t':'maprst'}],'mr',60)
    r=ab.run([{'t':'clonexf','hs':hs,'d':[dx,0]}],'c'+key,300)
    m=re.search(r'clonexf\s+(.*)',r); M[key]=dict(p.split('>') for p in m.group(1).split()); print(key,len(M[key]))
json.dump(M,open('w/map38.json','w'))
ab.run([{'t':'save'}],'sv',200)
