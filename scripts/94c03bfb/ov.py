import fitz
d=fitz.open('sec5.pdf')
o=open('dc5/ov.txt','w',encoding='utf8')
for i,p in enumerate(d):
    sp=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                if s['text'].strip(): sp.append((fitz.Rect(s['bbox']),s['text'].strip(),l['dir']))
    for a in range(len(sp)):
        for b in range(a+1,len(sp)):
            ra,rb=sp[a][0],sp[b][0]
            ia=fitz.Rect(ra);ib=fitz.Rect(rb)
            gx=max(rb.x0-ra.x1,ra.x0-rb.x1); gy=max(rb.y0-ra.y1,ra.y0-rb.y1)
            g=max(gx,gy)
            if g<0.8:
                o.write('P%d gap=%.2f %r %r @%d,%d\n'%(i+1,g,sp[a][1],sp[b][1],ra.x0,ra.y0))
