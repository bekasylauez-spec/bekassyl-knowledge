import re,sys,json
def load(p):
    t=open(p,encoding='utf-8-sig',errors='replace').read()
    docs={}
    for m in re.finditer(r'\(\s*(\d+)/(.*?)\)',t,re.S): docs.setdefault(int(m.group(1)),m.group(2))
    els=[[int(v) for v in s.split()] for s in docs[1].split('/') if s.strip()]
    nodes=[[float(v) for v in s.split()[:3]] for s in docs[4].split('/') if s.strip()]
    return els,nodes,docs
if __name__=='__main__':
    sys.path.insert(0,sys.argv[1]); import csvread
    els,nodes,docs=load(sys.argv[2]); print(len(els),len(nodes))
    g,r=csvread.load(sys.argv[3])
    out={}
    for gi in ['1','2','20','147']:
        es=sorted({x['el'] for x in r if x['g']==gi})
        lst=[]
        for e in es:
            t,st,*nd=els[e-1]; a,b=nodes[nd[0]-1],nodes[nd[1]-1]
            rr=[x for x in r if x['el']==e and x['typ']!='*']
            asum=max(sum(x['au'])+sum(x['as_']) for x in rr)
            au=max(max(x['au']) for x in rr); as12=max(max(x['as_'][:2]) for x in rr); as34=max(max(x['as_'][2:]) for x in rr)
            asw=max(max(x['asw']) for x in rr)
            lst.append(dict(el=e,st=st,a=a,b=b,asum=round(asum,2),au=au,as12=as12,as34=as34,asw=asw))
        out[gi]=lst
        for l in lst: print(gi,l['el'],l['st'],[round(v,3) for v in l['a']],[round(v,3) for v in l['b']],l['asum'],l['au'],l['as12'],l['as34'],l['asw'])
    json.dump(out,open(sys.argv[4],'w'),indent=0)
