import plot as P, fitz, os, shutil, gx
gx.run([{'t': 'save'}], 'sv')
shutil.copy(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда (Фм с выносками 19-21).dwg', gx.S + r'\w\snap.dwg')
Y = 455939
A2L = lambda n, x: P.plot(n, x, Y, x + 59400, Y + 42000)
A2P = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 59400, orient='_P')
A3L = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 29700, paper='ISO без полей A3 (297.00 x 420.00 мм)')
A3P = lambda n, x: P.plot(n, x, Y, x + 29700, Y + 42000, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
D = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж'
sets = {'Стена См-8 листы 5.29-5.34.pdf': [A2L('r29', 2209200), A3L('r30', 2268600), A2P('r31', 2310600), A2P('r32', 2352600), A2L('r33', 2394600), A3P('r34', 2454000)]}
for k, fs in sets.items():
    d = fitz.open()
    for f in fs: d.insert_pdf(fitz.open(f))
    d.save(os.path.join(D, k)); print(k, len(d))
