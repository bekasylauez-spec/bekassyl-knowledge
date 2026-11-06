import sys,re,json
def dec(b):
    try: return b.decode('utf-8')
    except: return b.decode('cp1251')
def load(p):
    groups={};rows=[];cur=None
    for raw in open(p,'rb').read().split(b'\n'):
        f=[dec(x).replace('﻿','').strip() for x in raw.rstrip(b'\r').split(b';')]
        if len(f)<4: continue
        if re.match(r'^\d+-S$',f[1]):
            cur=f[1][:-2]; groups[cur]=f[2]; continue
        if f[0]=='Id' or len(f)<20: continue
        try: e=int(f[4])
        except: continue
        rows.append(dict(g=f[2],el=e,sec=int(f[5]),typ=f[6],au=[float(x or 0) for x in f[10:14]],as_=[float(x or 0) for x in f[14:18]],asw=[float(x or 0) for x in f[19:21]],msg=f[9]))
    return groups,rows
if __name__=='__main__':
    g,r=load(sys.argv[1])
    for k,v in g.items(): print(k,v)
    print(len(r)); from collections import Counter; print(Counter(x['typ'] for x in r))
