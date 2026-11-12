import fitz,re
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for n in range(22,38):
    p=d[n-1]
    ws=p.get_text("words")
    out=[(w[4],round(w[0]/p.rect.width,2),round(w[1]/p.rect.height,2)) for w in ws if re.fullmatch(r'\d{1,2}[а-г]?',w[4]) and w[1]/p.rect.height<0.25 and w[0]/p.rect.width<0.2]
    print(n,"sheet",n-6,out[:12])
    t=[w[4] for w in ws if re.search(r'^\d+[а-г]?/\d+$',w[4])]
    print("  slash",t)
