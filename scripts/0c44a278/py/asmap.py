import pickle,math,collections,json
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
els,nodes=pickle.load(open(S+r'\lira.pkl','rb'))
raw=open(S+r'\as.csv','rb').read().decode('cp1251')
AS=collections.defaultdict(lambda:[0,0,0,0]); msg={}
for l in raw.splitlines()[1:]:
    f=l.split(';')
    if len(f)<12 or not f[1].isdigit():
        if len(f)>7 and f[1].endswith('-R'): msg[int(f[4])]=f[7].encode('cp1251','replace').decode('utf-8','replace').strip('\ufeff')
        continue
    if f[1]!='1': continue
    e=int(f[4]); v=[float(x) for x in f[8:12]]
    AS[e]=[max(a,b) for a,b in zip(AS[e],v)]
out={}
for z in (4.5,7.0):
    L=[]
    for e,v in AS.items():
        r=els[e-1]; ns=[nodes[int(i)-1] for i in r[2:]]
        if abs(ns[0][2]-z)>0.01 or any(abs(n[2]-z)>0.01 for n in ns): continue
        pts=[(n[0],n[1]) for n in ns]; cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        L.append(dict(e=e,c=(cx,cy),p=pts,a=v))
    out[str(z)]=L
    print(z,len(L),'max',[max(d['a'][k] for d in L) for k in range(4)])
    for e,m in msg.items():
        for d in L:
            if d['e']==e: print('  MSG',e,[round(c,2) for c in d['c']],m,d['a'])
json.dump(out,open(S+r'\as.json','w'))
