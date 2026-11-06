import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from common import *
AN=gx.S+r'\an\an.dwg'; AX,AY=-232571.9,411799.3
gx.run([dict(t='listfile',file=AN,win=[AX,AY,AX+31500,AY+14850])],'lf'); A=gx.log().splitlines()
relist(0); B=open(os.path.join(gx.S,'w','l61.txt'),encoding='utf-8-sig').read().splitlines()
def parse(L,ox,oy):
    out=[]
    for l in L:
        f=l.split('\t')
        if len(f)<5 or f[0]!='L' or f[1] not in('LINE','LWPOLYLINE') or not f[4].startswith('E') or 'NaN' in f[4]: continue
        e=[float(v) for v in f[4][1:].split(',')]
        out.append((f[1],f[2],f[3],(e[0]-ox,e[1]-oy,e[2]-ox,e[3]-oy)))
    return out
a=parse(A,AX,AY); b=parse(B,172179,455939)
miss=[]
for t,h,lay,e in a:
    if e[1]>10500 and e[0]<28000: continue
    if not any(all(abs(e[i]-f[3][i])<15 for i in range(4)) for f in b):
        miss.append((t,h,lay,[round(v) for v in e]))
print(len(a),len(b),len(miss))
for m in miss: print(m)
