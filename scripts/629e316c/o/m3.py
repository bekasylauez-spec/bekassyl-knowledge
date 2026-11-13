import fitz
d=fitz.open('km.pdf'); p=d[5]
segs=[]
for dr in p.get_drawings():
    for it in dr['items']:
        if it[0]=='l':
            a,b=it[1],it[2]; segs.append((a.x,a.y,b.x,b.y,dr.get('width') or 0))
# lower dims of section 3-3: y range 780..850pt ; scale 1:40 => 14.11 mm/pt
k=0.3528*40
for s in segs:
    L=abs(s[3]-s[1])
    if abs(s[0]-s[2])<0.1 and 30<L<120 and s[1]>740 and s[4]<0.3 and s[0]<420: print('V x=%.1f y %.1f-%.1f'%(s[0],s[1],s[3]))
for s in segs:
    L=abs(s[2]-s[0])
    if abs(s[1]-s[3])<0.1 and L>100 and s[1]>760 and s[0]<420 and s[4]<0.3: print('H y=%.1f x %.1f-%.1f L=%.1f -> %.0f mm'%(s[1],s[0],s[2],L,L*k))
