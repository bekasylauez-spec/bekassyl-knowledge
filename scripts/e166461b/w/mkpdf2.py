import plot as P, fitz, os
A2 = lambda n, x: P.plot(n, x, 455939, x + 59400, 497939)
A3 = lambda n, x: P.plot(n, x, 455939, x + 29700, 497939, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
fs = [A2('p6', 1100900), A2('p7', 1160300), A2('p8', 1219700), A3('p9', 1279100)]
d = fitz.open()
for f in fs: d.insert_pdf(fitz.open(f))
out = os.path.join(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж', 'Стена См-2 листы 5.6-5.9 (засечки, скобы, спецификация).pdf')
d.save(out); print(out, len(d))
