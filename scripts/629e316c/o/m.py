import fitz
d=fitz.open('km.pdf'); p=d[4]
# scale: dim 9650 mm; find thin horizontal long lines & verticals
segs=[]
for dr in p.get_drawings():
    for it in dr['items']:
        if it[0]=='l':
            a,b=it[1],it[2]; segs.append((a.x,a.y,b.x,b.y,dr.get('width')))
print(len(segs))
# 6.4 level horizontal line: y of text +6.400 ; find lines near x 54..100 pt horizontally
pt=lambda px:px/190*72
# vertical line near x = q5_2 370px => pt = 0.48*842 + 370/2.639
x=0.48*842+370/190*72
print('x dim',x)
for s in segs:
    if abs(s[0]-x)<1.5 and abs(s[2]-x)<1.5 : print('V',[round(v,1) for v in s])
# horizontal lines that start/end near x
for s in segs:
    if abs(s[1]-s[3])<0.05 and (s[0]<x+3 and s[2]>x-3) and abs(s[2]-s[0])<80 and 100<s[1]<250: print('H',[round(v,1) for v in s])
