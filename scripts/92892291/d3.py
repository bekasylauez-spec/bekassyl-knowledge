import ext,json,ab
SH=json.load(open('sheets.json'))
E=ext.load('w/ext.txt')
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
T=[(sheet(e.cx,e.cy),e.h) for e in E if e.dxf=='ACAD_TABLE']
ops=[{'t':'tdump','h':h} for s,h in T]
o=ab.run(ops,'td',wait=600)
open('w/tables.txt','w',encoding='utf-8').write(o)
json.dump(T,open('w/tables.json','w'))
print(T)
