import sys, json; sys.path.insert(0, 'st'); sys.path.insert(0, 'wl')
from plotan import plot_file
from common import frame, F
import plot as P
dwg = r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\5.1.Стена См-1...См-6.dwg'
k, i, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
x0, y0, x1, y1 = F[k][i][:4]; w, h = x1 - x0, y1 - y0
if len(sys.argv) > 4: w, h = float(sys.argv[4]), float(sys.argv[5]); x1, y1 = x0 + w, y0 + h
pdf = plot_file(dwg, name, x0, y0, x1, y1, paper='ISO без полей A1 (841.00 x 594.00 мм)' if max(w, h) > 60000 else 'ISO без полей A2 (594.00 x 420.00 мм)', orient='_L' if w >= h else '_P')
P.png(pdf, P.S + r'\w\%s.png' % name, 80)
for q, cl in enumerate([(0, 0, .5, .5), (.5, 0, 1, .5), (0, .5, .5, 1), (.5, .5, 1, 1)]): P.png(pdf, P.S + r'\w\%s_q%d.png' % (name, q), 170, cl)
print(pdf)
