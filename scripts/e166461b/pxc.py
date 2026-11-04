import sys, collections
L=open(sys.argv[1],encoding='cp1251',errors='replace').read().split('\n')
L=[x.strip() for x in L]
# classes
cls=[]; i=0
while i<len(L)-1:
    if L[i]=='0' and L[i+1]=='CLASS':
        j=i+2; name=None
        while not (L[j]=='0'): 
            if L[j]=='1': name=L[j+1]
            j+=2
        cls.append(name); i=j
    elif L[i]=='2' and L[i+1]=='ENTITIES': break
    else: i+=2 if False else 1
res=collections.defaultdict(list)
i=0
while i<len(L)-1:
    if L[i]=='0' and L[i+1]=='ACAD_PROXY_ENTITY':
        j=i+2; h=None; cid=None; lay=None
        while L[j]!='0':
            if L[j]=='5' and h is None: h=L[j+1]
            if L[j]=='91' and cid is None: cid=int(L[j+1])
            if L[j]=='8' and lay is None: lay=L[j+1]
            j+=2
        res[cls[cid-500] if cid and 0<=cid-500<len(cls) else cid].append((h,lay)); i=j
    else: i+=1
for k,v in res.items(): print(k,len(v),v[:8])
