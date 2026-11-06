import sys
X0,Y0=-691502.7,-1749172.2
def load(f,x0=X0,y0=Y0,W=29700):
    R=[]
    for line in open(f,encoding='utf-8-sig'):
        p=line.rstrip('\n').split('|')
        if len(p)<8 or p[3]=='': continue
        bb=[float(v) for v in p[3:7]]
        r=dict(h=p[0],t=p[1],lay=p[2],x0=bb[0]-x0,y0=bb[1]-y0,x1=bb[2]-x0,y1=bb[3]-y0,info='|'.join(p[7:-1]),sp=p[-1])
        if r['x1']<-50 or r['x0']>W+50: continue
        R.append(r)
    return R
if __name__=='__main__':
    R=load(sys.argv[1])
    for r in sorted(R,key=lambda r:(r['t'],r['x0'],r['y0'])):
        if r['t'] in('LWPOLYLINE',) and r['lay']=='диам10': continue
        print(r['h'],r['t'],r['lay'],round(r['x0']),round(r['y0']),round(r['x1']),round(r['y1']),r['info'][:110])
