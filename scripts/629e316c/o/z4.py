import fitz
d=fitz.open('km.pdf')
def z(pg,x0,y0,x1,y1,name,dpi=500):
    d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(name)
z(8,575,160,650,200,'z8_pp.png')
z(1,830,0,1080,45,'z1_top.png',dpi=300)
# frame coords page1
p=d[0]
for dr in p.get_drawings():
    for it in dr['items']:
        if it[0]=='re' and (it[1].width>1500): print('rect',it[1])
        if it[0]=='l' and abs(it[1].y-it[2].y)<0.1 and abs(it[1].x-it[2].x)>1000 and it[1].y<60: print('hline',it[1],it[2],dr.get('width'))
for b in p.get_text('dict')['blocks']:
    for l in b.get('lines',[]):
        t=''.join(s['text'] for s in l['spans'])
        if 'АНТИКОР' in t: print(t, l['bbox'])
