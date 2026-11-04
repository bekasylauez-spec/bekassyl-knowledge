# usage: python -X utf8 crop.py <page> <x0> <y0> <x1> <y1> [zoom]  (fractions 0..1 of page) -> png/cNNN_x.png
import fitz, sys, os
S = os.path.dirname(os.path.abspath(__file__))
pdf = r"D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\КЖ Чертеж БЦ Байтурсынова Блок 1.pdf"
n = int(sys.argv[1]); fx0, fy0, fx1, fy1 = map(float, sys.argv[2:6]); z = float(sys.argv[6]) if len(sys.argv) > 6 else 4
d = fitz.open(pdf); p = d[n - 1]; r = p.rect
clip = fitz.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height, r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
pm = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip)
os.makedirs(os.path.join(S, "png"), exist_ok=True)
out = os.path.join(S, "png", f"c{n:03d}_{fx0:.2f}_{fy0:.2f}.png"); pm.save(out); print(out, pm.width, pm.height)
