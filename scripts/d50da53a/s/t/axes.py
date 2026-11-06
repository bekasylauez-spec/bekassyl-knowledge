import ext,json
SH=json.load(open('sheets.json'))
_E=None
def E():
    global _E
    if _E is None: _E=ext.load('w/ext.txt')
    return _E
def ins(e,s,p=0):
    a,b,c,d=SH[s]; return e.bb and a-p<=e.cx<=c+p and b-p<=e.cy<=d+p
def axes(s):
    cl=[e for e in E() if ins(e,s) and e.dxf=='SPDSCONSTRUCTIONLINE']
    H=sorted([e for e in cl if e.bb[2]-e.bb[0]>e.bb[3]-e.bb[1]],key=lambda e:e.cy)
    V=sorted([e for e in cl if e.bb[2]-e.bb[0]<e.bb[3]-e.bb[1]],key=lambda e:e.cx)
    return [round(e.cx,3) for e in V],[round(e.cy,3) for e in H],H,V
if __name__=='__main__':
    import sys
    for s in sys.argv[1:]:
        X,Y,H,V=axes(s); print(s,'X',X[:3],'..',len(X),'Y',Y)
        for e in H+V: print('  ',e.h,[round(v) for v in e.bb], e.sp[:4])
