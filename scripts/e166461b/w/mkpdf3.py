import plot as P, fitz, os
A2 = lambda n, x: P.plot(n, x, 455939, x + 59400, 497939)
A3P = lambda n, x: P.plot(n, x, 455939, x + 29700, 497939, paper='ISO без полей A3 (297.00 x 420.00 мм)', orient='_P')
A3L = lambda n, x: P.plot(n, x, 455939, x + 42000, 485639, paper='ISO без полей A3 (420.00 x 297.00 мм)')
D = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж'
sets = {'Стена См-1 листы 5.1-5.5.pdf': [A2('q1', 764100), A2('q2', 823500), A2('q3', 882900), A3L('q4', 942300), A3P('q5', 984300)],
        'Стена См-2 листы 5.6-5.9.pdf': [A2('q6', 1014000), A2('q7', 1073400), A2('q8', 1132800), A3P('q9', 1192200)],
        'Стена См-3 листы 5.10-5.13.pdf': [A2('q10', 1221900), A2('q11', 1281300), A2('q12', 1340700), A3P('q13', 1400100)]}
for k, fs in sets.items():
    d = fitz.open()
    for f in fs: d.insert_pdf(fitz.open(f))
    d.save(os.path.join(D, k)); print(k, len(d))
P.png(fs[0], P.S + r'\w\q10.png', 40)
