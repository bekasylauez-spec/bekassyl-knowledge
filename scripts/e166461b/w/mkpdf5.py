import plot as P, fitz, os, shutil, gx
gx.run([{'t': 'save'}], 'sv')
shutil.copy(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда (Фм с выносками 19-21).dwg', gx.S + r'\w\snap.dwg')
A2 = lambda n, x: P.plot(n, x, 455939, x + 59400, 497939)
A3P = lambda n, x: P.plot(n, x, 455939, x + 29700, 497939, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
D = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж'
sets = {'Стена См-4 листы 5.14-5.16.pdf': [A2('q14', 1429800), A2('q15', 1489200), A3P('q16', 1548600)],
        'Стена См-5 листы 5.17-5.19.pdf': [A2('q17', 1578300), A2('q18', 1637700), A3P('q19', 1697100)]}
for k, fs in sets.items():
    d = fitz.open()
    for f in fs: d.insert_pdf(fitz.open(f))
    d.save(os.path.join(D, k)); print(k, len(d))
