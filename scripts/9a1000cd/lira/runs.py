import pickle,collections
H=pickle.load(open('blines.pkl','rb'))
AX={54.65:'9',64.15:'10',73.65:'11',79.65:'12',86.25:'13'}
AY={0:'А',7.0:'Б',10.5:'В',15.5:'Г',16.5:'Д',21.0:'Е',22.0:'Ж',28.0:'И',29.0:'К'}
def nx(v):
    v=v+1.2
    for k,n in AX.items():
        if abs(k-v)<0.45: return n
    return '%.2f'%v
def ny(v):
    v=v+1.35
    for k,n in AY.items():
        if abs(k-v)<0.05: return n
    return '%.2f'%v
def merge(rs):
    rs=sorted(rs); out=[[rs[0][0],rs[0][1]]]
    for a,b,_ in rs[1:]:
        if a<=out[-1][1]+0.001: out[-1][1]=max(out[-1][1],b)
        else: out.append([a,b])
    return out
lv=collections.defaultdict(list)
for k,v in H.items():
    d,z,c,s=k
    if d=='?': lv[z].append(('диаг',s,len(v))); continue
    for a,b in merge(v):
        if d=='X': lv[z].append(('ось '+ny(c),s,'%s–%s'%(nx(a),nx(b)),round(b-a,2)))
        else: lv[z].append(('ось '+nx(c),s,'%s–%s'%(ny(a),ny(b)),round(b-a,2)))
for z in sorted(lv):
    print('== %.3f'%z,len(lv[z]))
    for r in lv[z]: print('  ',r)
