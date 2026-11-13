import fitz
d=fitz.open('km.pdf')
for i,p in enumerate(d):
    W,H=p.rect.width,p.rect.height
    x0,y0,x1,y1=56.69,14.17,W-14.17,H-14.17
    print('--- page',i+1,'frame',round(x0),round(y0),round(x1),round(y1))
    n=0
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            bb=fitz.Rect(l['bbox']); t=''.join(s['text'] for s in l['spans'])
            if bb.x0<x0-1 or bb.x1>x1+1 or bb.y0<y0-1 or bb.y1>y1+1:
                if i==0 and bb.x1<x0+2: continue
                if bb.y0>y1 and 'Формат' in t or t.strip() in('A3','A2'): continue
                print(' TEXT out',ascii(t),[round(v,1) for v in bb])
    for dr in p.get_drawings():
        r=dr['rect']
        if r.width>W*0.9 or r.height>H*0.9: continue
        if r.x0<x0-1.5 or r.x1>x1+1.5 or r.y0<y0-1.5 or r.y1>y1+1.5:
            if i==0 and r.x1<x0+2: continue
            if r.y0>y1-1: continue
            n+=1
            if n<8: print(' DRAW out',[round(v,1) for v in r], dr.get('width'))
    print(' draw-out count',n)
