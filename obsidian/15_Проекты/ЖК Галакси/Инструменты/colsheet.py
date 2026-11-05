import gx, os, json
def listwin(X0,Y0,w=59400,h=42000):
    gx.run([{'t':'list','win':[X0,Y0,X0+w,Y0+h]}],'lst')
    R=[]
    for l in open(os.environ['TEMP']+'/gx_log.txt',encoding='utf-8').read().splitlines():
        if not l.startswith('L\t'): continue
        r=l.split('\t'); e=[float(v) for v in r[4][1:].split(',')]
        sp=[tuple(float(c) for c in p.split(',')) for p in r[5:]]
        R.append(dict(t=r[1],h=r[2],lay=r[3],x0=e[0]-X0,y0=e[1]-Y0,x1=e[2]-X0,y1=e[3]-Y0,sp=[(p[0]-X0,p[1]-Y0) for p in sp]))
    return R
if __name__=='__main__':
    import sys
    X0,Y0=float(sys.argv[1]),float(sys.argv[2])
    R=listwin(X0,Y0); json.dump(R,open(sys.argv[3],'w'),ensure_ascii=False)
    print(len(R))
