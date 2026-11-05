import plot as P, fitz, os, shutil, gx, sys
gx.run([{'t': 'save'}], 'sv')
shutil.copy(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда (Фм с выносками 19-21).dwg', gx.S + r'\w\snap.dwg')
Y = 455939
A2L = lambda n, x: P.plot(n, x, Y, x + 59400, Y + 42000)
A2P = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 59400, orient='_P')
A3L = lambda n, x: P.plot(n, x, Y, x + 42000, Y + 29700, paper='ISO без полей A3 (297.00 x 420.00 мм)')
A3P = lambda n, x: P.plot(n, x, Y, x + 29700, Y + 42000, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
D = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж'
ALL = {'9': ('Стена См-9 листы 5.36-5.38.pdf', lambda: [A2L('s36', 2483700), A2L('s37', 2543100), A3P('s38', 2602500)])}
for k in sys.argv[1:]:
    name, f = ALL[k]; fs = f(); d = fitz.open()
    for x in fs: d.insert_pdf(fitz.open(x))
    d.save(os.path.join(D, name)); print(name, len(d))
