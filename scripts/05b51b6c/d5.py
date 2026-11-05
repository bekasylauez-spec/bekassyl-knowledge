import ext,json,re
SH=json.load(open('sheets.json'))
E=ext.load('w/ext.txt')
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
pat=re.compile(r'(%%[cC]|∅|Ø|Ф|U\+2205|H5|Н5)')
want={'3.2','3.3','3.4','3.5','3.6','3.7','4.1','6.1','6.2','2.5','3.1'}
for e in E:
    if not e.bb: continue
    s=sheet(e.cx,e.cy)
    if s in want and e.dxf in('MTEXT','TEXT','DIMENSION') and pat.search(e.txt()):
        print(s,e.h,e.dxf,repr(e.txt()[:70]))
for l in open('w/notes.txt',encoding='utf-8'):
    p=l.rstrip('\n').split('\t')
    if p[0]!='N': continue
    ex=[q for q in p if q.startswith('E')]
    a=[float(v) for v in ex[-1][1:].split(',')]
    s=sheet((a[0]+a[2])/2,(a[1]+a[3])/2)
    if s in want and pat.search(p[3]+p[4]): print(s,p[1],p[2][-4:],repr(p[3]),repr(p[4]))
