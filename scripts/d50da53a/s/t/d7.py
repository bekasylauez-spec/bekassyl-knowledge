import json,sys
SH=json.load(open('sheets.json'))
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
for l in open('w/notes.txt',encoding='utf-8'):
    p=l.rstrip('\n').split('\t')
    if p[0]!='N': continue
    ex=[q for q in p if q.startswith('E')]
    if not ex: print('noext',p[1:5]); continue
    a=[float(v) for v in ex[-1][1:].split(',')]
    s=sheet((a[0]+a[2])/2,(a[1]+a[3])/2)
    if s in sys.argv[1:]: print(s,p[1],p[2][-4:],repr(p[3]),repr(p[4]))
