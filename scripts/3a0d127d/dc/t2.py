import pymupdf,re,sys
sys.stdout.reconfigure(encoding="utf-8")
doc=pymupdf.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(doc):
    ws=p.get_text("words")
    for w in ws:
        if re.fullmatch(r"\d{3,}[,.]\d+",w[4]) and w[4]!="24379.1":
            print(i+1,w[4],[round(x) for x in w[:4]])
    # stamp: words in bottom-right
    R=p.rect
    st=[w[4] for w in ws if w[0]>R.width-520*0+ R.width*0.7 and w[1]>R.height-200 and re.fullmatch(r"[\d\-]{1,5}",w[4])]
    print(i+1,"stamp nums",st[:8])
