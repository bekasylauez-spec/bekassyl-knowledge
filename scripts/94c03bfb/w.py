import fitz,re
for n in range(1,14):
    pg=fitz.open(r'D:\_claude_work\Kasymova\revit\_check\v10\s2.%d.pdf'%n)[0]
    for w in pg.get_text('words'):
        t=w[4]
        if re.search(r'Фраг|Разрез|^\d-\d$|34000|^\d$',t):
            print(n,[round(v) for v in w[:4]],t)
