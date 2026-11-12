import fitz,re
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d):
    ws=p.get_text("words")
    print("=== PAGE",i+1,len(ws),"words, dr:",len(p.get_drawings()))
    # list short tokens
    from collections import Counter
    c=Counter(w[4] for w in ws)
    print([ (k,v) for k,v in c.items() if re.search(r'^(У\d|\d+[а-б]?/\d+|\d-\d|[1-9]|У\d+[а-я]?)$',k)])
