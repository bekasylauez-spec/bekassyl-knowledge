# save main DWG, snapshot, plot sheet at X (A2), crops: python w/shot.py name X x0,y0,x1,y1 [...]
import sys, shutil, gx, plot as P
gx.run([{'t': 'save'}], 'sv')
shutil.copy(r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда (Фм с выносками 19-21).dwg', gx.S + r'\w\snap.dwg')
n, X = sys.argv[1], float(sys.argv[2])
pdf = P.plot(n, X, 455939, X + 59400, 497939)
for i, c in enumerate(sys.argv[3:]):
    P.png(pdf, gx.S + r'\w\%s_%d.png' % (n, i), 190, tuple(float(v) for v in c.split(',')))
print('ok')
