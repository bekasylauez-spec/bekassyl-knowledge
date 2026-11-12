import fitz,re
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d,1):
    if i<7: continue
    W,H=p.rect.width,p.rect.height
    ws=[w for w in p.get_text("words") if w[1]<H-170 or w[0]<W-560]
    odd=[]
    for w in ws:
        t=w[4]
        if re.search(r"\d[.,]\d",t) and not re.search(r"\+\d,\d{3}|−\d|-\d,\d{3}|\d,\d{3}",t): odd.append((t,round(w[0]),round(w[1])))
        if re.fullmatch(r"У\w*|[0-9]{1,2}",t) is None and t.startswith("У") and len(t)<5: odd.append((t,round(w[0]),round(w[1])))
    print(i,odd[:40])
