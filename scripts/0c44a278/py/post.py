import pickle,math
import geom, design as D0
S=geom.S
LAP={10:610,12:730,14:860,16:980,18:1100,20:1220,22:1350,25:1530}
res,RS=pickle.load(open(S+r'\design.pkl','rb'))
for z in res:
    for f in res[z]:
        out=[]
        for Z in res[z][f]:
            Z['s']=int(round(Z['s']/10)*10); Z['e']=int(round(Z['e']/10)*10); Z['L']=Z['e']-Z['s']
            # round length down to 50 (bars clipped by an edge end 25..75 from it)
            Z['L']=int(Z['L']//50*50); Z['e']=Z['s']+Z['L']
            if Z['L']<1000: continue
            if Z['L']<=11700: out.append(Z); continue
            k=math.ceil((Z['L']-LAP[Z['d']])/(11700-LAP[Z['d']])); 
            piece=math.ceil(((Z['L']+(k-1)*LAP[Z['d']])/k)/50)*50
            s=Z['s']
            for i in range(k):
                e=min(Z['e'],s+piece)
                if i==k-1: s=Z['e']-piece; e=Z['e']
                q=dict(Z); q['s']=s; q['e']=e; q['L']=e-s; out.append(q)
                s=e-LAP[Z['d']]
        res[z][f]=out
pickle.dump((res,RS),open(S+r'\design.pkl','wb'))
