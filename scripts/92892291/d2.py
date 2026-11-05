import ext,json,re,sys
SH=json.load(open('sheets.json'))
E=ext.load('w/ext.txt')
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
from collections import Counter,defaultdict
cnt=defaultdict(Counter)
for e in E:
    if not e.bb: continue
    t=e.txt()
    for m in re.finditer(r'(%%[cC]|∅|Ø|\\U\+2205|Ф|ф)\s*(\d{1,2})\b',t):
        cnt[sheet(e.cx,e.cy)][m.group(2)]+=1
for l in open('w/notes.txt',encoding='utf-8'):
    p=l.split('\t')
    if p[0]!='N': continue
    ex=[q for q in p if q.startswith('E')]
    if not ex: continue
    a=[float(v) for v in ex[-1][1:].split(',')]
    s=sheet((a[0]+a[2])/2,(a[1]+a[3])/2)
    for m in re.finditer(r'(%%[cC]|∅|Ø|Ф)\s*(\d{1,2})\b',p[3]+' '+p[4]):
        cnt[s]['N'+m.group(2)]+=1
for k in SH:
    if cnt[k]: print(k,dict(cnt[k]))
