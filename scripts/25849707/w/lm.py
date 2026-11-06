import re,collections,pickle
D=r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Data\бдм блок 1 униф.txt'
t=open(D,encoding='utf-8-sig').read()
def doc(n):
    m=re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S); return m.group(1)
els=[]
for r in doc(1).split('/'):
    v=r.split()
    if len(v)>=3: els.append((int(v[0]),int(v[1]),[int(x) for x in v[2:]]))
nodes=[]
for r in doc(4).split('/'):
    v=r.split()
    if len(v)>=3: nodes.append(tuple(float(x) for x in v[:3]))
# stiffness doc 3: blocks start with "N ..." first token = idx
st={}
cur=None
for r in doc(3).split('/'):
    v=r.split()
    if not v: continue
    if v[0]!='0': cur=int(v[0]); st[cur]={'raw':' '.join(v[:8])}
    elif len(v)>1 and cur: st[cur].setdefault('extra',[]).append(' '.join(v[1:]))
pickle.dump((els,nodes,st),open('lm.pkl','wb'))
print(len(els),len(nodes),len(st))
for k in sorted(st):
    print(k,st[k]['raw'][:60],st[k].get('extra'))
