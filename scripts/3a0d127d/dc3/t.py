import pymupdf,collections
d=pymupdf.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
for i,p in enumerate(d):
    c=collections.Counter(); fonts=collections.Counter()
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                if s['text'].strip():
                    c[round(s['size']*25.4/72/ (1 if True else 1),2)]+=1; fonts[s['font']]+=1
    print(i+1,dict(c),dict(fonts))
