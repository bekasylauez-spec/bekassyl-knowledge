import fitz
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d,1):
    W,H=p.rect.width,p.rect.height
    ws=[w for w in p.get_text("words") if w[0]>W-560 and w[1]>H-260]
    ws.sort(key=lambda w:(round(w[1]),w[0]))
    print(i,int(W),int(H),' | '.join(w[4] for w in ws)[:600])
