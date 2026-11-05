# per wall piece and storey: vertical Ø/step covering max(AS3,AS4) per face, horizontal Ø/step covering max(AS1,AS2)
import json,sys,math
C=json.load(open('arm/wall_cells.json'))
LEV=[-4.65,-0.1,3.95,7.1,10.25,13.4,16.55,19.7,23.2]
A=lambda d:math.pi*d*d/400
VOPT=[(12,200),(14,200),(16,200),(18,200),(12,100),(14,100),(16,100),(18,100),(20,100),(22,100),(25,100),(28,100),(32,100)]
HOPT=[(10,200),(12,200),(10,100),(12,100),(14,100),(16,100)]
def pick(req,opts):
    best=None
    for d,s in opts:
        a=A(d)*1000/s
        if a>=req-1e-6 and (best is None or a<best[2]): best=(d,s,a)
    return best
def design(ax,val,pieces):
    sel=[c for c in C if tuple(c['pl'])==(ax,val)]
    k0,k1=('x0','x1') if ax=='y' else ('y0','y1')
    out=[]
    for s in range(len(LEV)-2):
        row=[]
        for (a,b) in pieces:
            cs=[c for c in sel if LEV[s]-1e-3<=c['z0']<LEV[s+1]-1e-3 and c[k1]>a+1 and c[k0]<b-1]
            if not cs: row.append(None); continue
            rv=max(max(c['As'][2],c['As'][3]) for c in cs); rh=max(max(c['As'][0],c['As'][1]) for c in cs)
            row.append((round(rv,1),pick(rv,VOPT),round(rh,1),pick(rh,HOPT)))
        out.append((LEV[s],row))
    return out
if __name__=='__main__':
    P=[(0,1225),(5875,7725),(12325,14175),(18825,20050)]
    for lv,row in design('y',0,P):
        print('%6.2f'%lv,' | '.join('V%.1f→Ø%d/%d  H%.1f→Ø%d/%d'%(r[0],r[1][0],r[1][1],r[2],r[3][0],r[3][1]) if r else '-' for r in row))
