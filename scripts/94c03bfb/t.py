import fitz,itertools
for n in range(1,14):
    pg=fitz.open(r'D:\_claude_work\Kasymova\revit\_check\v10\s2.%d.pdf'%n)[0]
    sp=[]
    for b in pg.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                t=s['text'].strip()
                if t: sp.append((fitz.Rect(s['bbox']),t,l['dir']))
    hits=[]
    for (a,ta,da),(b,tb,db) in itertools.combinations(sp,2):
        i=a&b
        if i.is_valid and not i.is_empty and i.width*i.height>0.1*min(a.width*a.height,b.width*b.height):
            hits.append((round(a.x0),round(a.y0),ta,round(b.x0),round(b.y0),tb))
    print('PAGE',n,len(sp),'overlaps',len(hits))
    for h in hits: print('  ',h)
