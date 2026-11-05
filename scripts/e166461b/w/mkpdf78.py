import plot as P, fitz, os, shutil, gx
gx.run([{'t': 'save'}], 'sv')
shutil.copy(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда (Фм с выносками 19-21).dwg', gx.S + r'\w\snap.dwg')
Y = 455939
A2L = lambda n, x: P.plot(n, x, Y, x + 59400, Y + 42000)
A2P = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 59400, orient='_P')
A3L = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 29700, paper='ISO без полей A3 (297.00 x 420.00 мм)')
A3P = lambda n, x: P.plot(n, x, Y, x + 29700, Y + 42000, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
D = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж'
sets = {'Стена См-7 листы 5.24-5.29.pdf': [A2L('q24', 1934700), A3L('q25', 1994100), A2P('q26', 2036100), A2P('q27', 2078100), A3P('q28', 2120100), A2L('q29', 2149800)], 'Стена См-8 листы 5.30-5.35.pdf': [A2L('r30', 2209200), A3L('r31', 2268600), A2P('r32', 2310600), A2P('r33', 2352600), A2L('r34', 2394600), A3P('r35', 2454000)]}
for k, fs in sets.items():
    d = fitz.open()
    for f in fs: d.insert_pdf(fitz.open(f))
    d.save(os.path.join(D, k)); print(k, len(d))
