import fitz
d=fitz.open('km.pdf'); p=d[4]
segs=[]
for dr in p.get_drawings():
    for it in dr['items']:
        if it[0]=='l':
            a,b=it[1],it[2]; segs.append((a.x,a.y,b.x,b.y,dr.get('width')))
print('long verticals/horizontals thin:')
for s in segs:
    L=((s[0]-s[2])**2+(s[1]-s[3])**2)**.5
    if L>60 and (abs(s[0]-s[2])<0.1 or abs(s[1]-s[3])<0.1) and (s[4] or 0)<0.3:
        print([round(v,1) for v in s], round(L,1))
