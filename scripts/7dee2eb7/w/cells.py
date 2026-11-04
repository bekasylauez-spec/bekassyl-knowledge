import json
L=json.load(open('lmodel.json')); N=L['nodes']; E=L['els']; As=json.load(open('as.json'))
X0=174.15
def cells(z):
    out=[]
    for i,(t,s,nn) in enumerate(E):
        if t in(41,42,44) and s==39:
            zz=[N[n-1][2] for n in nn]
            if max(zz)-min(zz)<1e-3 and abs(zz[0]-z)<1e-3:
                xs=[(N[n-1][0]-X0)*1000 for n in nn]; ys=[N[n-1][1]*1000 for n in nn]
                out.append(dict(id=i+1,poly=list(zip(xs,ys)),x0=min(xs),x1=max(xs),y0=min(ys),y1=max(ys),cx=sum(xs)/len(xs),cy=sum(ys)/len(ys),As=As[str(i+1)][1]))
    return out
