import axes,ab,os,sys,json
from shapely.geometry import LineString, box
BAR,HD,VD,NOTE='37314A','3737B0','373B46','373165'
NA=(-141422.598+141763.431, -1720286.699+1720750.46)  # arrow - shelf origin
def zones(opening):
    Z=[]
    def add(kind,pos,L,bars):  # bars: list of (x0,y0,x1,y1)
        # clip bars by opening
        out=[]
        for b in bars:
            ls=LineString([(b[0],b[1]),(b[2],b[3])])
            if opening is not None and ls.intersects(opening):
                d=ls.difference(opening)
                if d.is_empty: continue
                segs=list(getattr(d,'geoms',[d])); s=max(segs,key=lambda g:g.length)
                if s.length<900: continue
                c=list(s.coords); out.append((c[0][0],c[0][1],c[-1][0],c[-1][1]))
            else: out.append(b)
        # group consecutive bars with equal length
        grp=[]
        for b in out:
            Lb=round(abs(b[2]-b[0])+abs(b[3]-b[1]))
            if grp and grp[-1][0]==Lb and len(grp[-1][1]) and abs((b[1]-grp[-1][1][-1][1]) if kind=='d' else (b[0]-grp[-1][1][-1][0]))<=201: grp[-1][1].append(b)
            else: grp.append([Lb,[b]])
        for Lb,bs in grp:
            if len(bs)<2: continue
            Z.append({'kind':kind,'L':Lb,'bars':bs,'pos':{2400:'2',1400:'3'}.get(Lb,'4')})
    for k in range(11):          # digit axes, bars horizontal
        xc=6000*k
        xa,xb=(xc-175,xc+1225) if k==0 else ((xc-1225,xc+175) if k==10 else (xc-1200,xc+1200))
        for j in range(2):
            ys=[6000*j+300+200*n for n in range(28)]
            add('d',None,None,[(xa,y,xb,y) for y in ys])
    for j in range(3):           # letter axes, bars vertical
        yc=6000*j
        ya,yb=(yc-175,yc+1225) if j==0 else ((yc-1225,yc+175) if j==2 else (yc-1200,yc+1200))
        for i in range(10):
            xs=[6000*i+300+200*n for n in range(28)]
            add('l',None,None,[(x,ya,x,yb) for x in xs])
    return Z
def ops(sheet,opening,tag):
    X,Y,_,_=axes.axes(sheet); X=[x for x in X if any(abs(abs(x-x2)-6000)<1 for x2 in X)]; x1,yA=X[0],Y[0]
    P=lambda x,y:[x+x1,y+yA]
    Z=zones(opening); O=[]; n=0
    for z in Z:
        bs=z['bars']; f,l=bs[0],bs[-1]; N=len(bs)-1
        for b,s in ((f,'a'),(l,'b')):
            t='%s%d%s'%(tag,n,s); O.append({'t':'clone','h':BAR,'tag':t}); O.append({'t':'plset','h':t,'p':[P(b[0],b[1]),P(b[2],b[3])]})
        t='%s%dd'%(tag,n); txt='200х%d=%d'%(N,200*N)
        if z['kind']=='d':
            xd=max(f[0],f[2])+300 if f[2]-f[0]>0 else f[0]+300
            if min(f[0],f[2])<-100: xd=max(f[0],f[2])+300
            elif max(f[0],f[2])>60100: xd=min(f[0],f[2])-300
            O.append({'t':'clone','h':VD,'tag':t}); O.append({'t':'dimpts','h':t,'p1':P(f[2],f[1]),'p2':P(f[2],l[1]),'dl':P(xd,f[1])}); O.append({'t':'dimtext','h':t,'s':txt})
            T=(min(l[0],l[2])+200,l[1])
        else:
            yd=max(f[1],f[3])+300
            if max(f[1],f[3])>12100: yd=min(f[1],f[3])-300
            O.append({'t':'clone','h':HD,'tag':t}); O.append({'t':'dimpts','h':t,'p1':P(f[0],f[3]),'p2':P(l[0],f[3]),'dl':P(f[0],yd)}); O.append({'t':'dimtext','h':t,'s':txt})
            T=(l[0],min(l[1],l[3])+200)
        nt=P(T[0]-NA[0],T[1]-NA[1]); a=P(*T)
        O.append({'t':'clonexf','hs':[NOTE],'d':[a[0]-(-141422.598),a[1]-(-1720286.699)],'pre':'%s%dn_'%(tag,n)})
        O.append({'t':'mcset','h':'%s%dn_%s'%(tag,n,NOTE),'set':{'FirstLine':'%s(ф12) L=%d'%(z['pos'],z['L']),'SecondLine':'ш.200'}})
        n+=1
    return O,Z
if __name__=='__main__':
    op=box(48000,0,50750,4050)
    O1,Z1=ops('7.4',op,'D74_'); O2,Z2=ops('7.7',None,'D77_')
    for nm,Z in (('Пм-2',Z1),('Пм-3',Z2)):
        from collections import Counter
        c=Counter(); 
        for z in Z: c[(z['pos'],z['L'])]+=len(z['bars'])
        print(nm,len(Z),dict(c), 'kg', round(sum(L/1000*q*0.888 for (p,L),q in c.items()),1))
    json.dump({'Z1':[[z['pos'],z['L'],len(z['bars'])] for z in Z1],'Z2':[[z['pos'],z['L'],len(z['bars'])] for z in Z2]},open('w/dopz.json','w'))
    if len(sys.argv)>1:
        ab.run(O1+O2+[{'t':'save'}],'dop',wait=1800); print(open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read()[-300:])
