import re,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
t=open(sys.argv[1],encoding='utf-8-sig').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)\s*/(.*?)\n\s*\)',t,re.S):
    docs.setdefault(int(m.group(1)),m.group(2))
def recs(s): return [r.split() for r in s.replace('\n',' ').split('/') if r.strip()]
el=recs(docs[1]); nd=[list(map(float,r)) for r in recs(docs[4])]
print('nodes',len(nd),'elems',len(el))
import json
json.dump({'el':el,'nd':nd},open(sys.argv[2],'w'))
st=collections.defaultdict(list)
for i,r in enumerate(el,1): st[(r[0],r[1])].append(i)
for k,v in st.items(): print('type,stiff',k,len(v))
xs=sorted(set(round(n[0],3) for n in nd)); ys=sorted(set(round(n[1],3) for n in nd)); zs=sorted(set(round(n[2],3) for n in nd))
print('X',xs);print('Y',ys);print('Z',zs)
l6=recs(docs[6]); v7={int(r[0]):r[1:] for r in recs(docs[7])}
g=collections.defaultdict(list)
for r in l6: g[tuple(r[1:])].append(int(r[0]))
for k,v in sorted(g.items(),key=lambda x:(int(x[0][3]),x[0])):
    print(k,'val',v7[int(k[2])],'n',len(v),v[:6],'...' if len(v)>6 else '')
