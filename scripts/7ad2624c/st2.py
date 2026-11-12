import fitz
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d,1):
    L=[l.strip() for l in p.get_text().split('\n')]
    try:
        k=L.index('Лист', L.index('Стадия')) if False else None
    except: pass
    idx=[j for j,l in enumerate(L) if l=='П']
    s=' / '.join(L[idx[0]+1:idx[0]+5]) if idx else 'NOP'
    print(i,s, '| ГИП' , 'Сейлханов Е.' in L, 'Кулбай Ш.' in L,'Вислов И.' in L,'Турлыбекова А.' in L)
