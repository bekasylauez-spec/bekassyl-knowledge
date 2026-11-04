# usage: python -X utf8 render.py <first> <last> [zoom]  -> scratchpad/png/pNNN.png
import fitz, sys, os
S = os.path.dirname(os.path.abspath(__file__))
pdf = r"D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\КЖ Чертеж БЦ Байтурсынова Блок 1.pdf"
a, b = int(sys.argv[1]), int(sys.argv[2]); z = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
os.makedirs(os.path.join(S, "png"), exist_ok=True)
d = fitz.open(pdf)
for i in range(a, b + 1):
    p = d[i - 1]; pm = p.get_pixmap(matrix=fitz.Matrix(z, z))
    out = os.path.join(S, "png", f"p{i:03d}.png"); pm.save(out); print(out, pm.width, pm.height)
