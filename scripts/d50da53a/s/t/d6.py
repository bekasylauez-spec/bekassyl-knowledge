import ext,json,re,sys
SH=json.load(open('sheets.json'))
E=ext.load('w/ext.txt')
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
from collections import Counter
for s in sys.argv[1:]:
    c=Counter(e.dxf for e in E if e.bb and sheet(e.cx,e.cy)==s); print(s,dict(c))
    for e in E:
        if e.bb and sheet(e.cx,e.cy)==s and e.dxf in ('MULTILEADER','INSERT','TEXT','MTEXT') and re.search(r'(20|25|16|12|14|H5|Н5)',e.info): print('  ',e.h,e.dxf,e.info[:90])
