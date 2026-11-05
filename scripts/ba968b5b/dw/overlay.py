import json, sys, pymupdf as fitz
sys.stdout.reconfigure(encoding='utf-8')
SH = json.load(open(r'D:\РАБОЧКА\От Маке\Завод\АБК\_Инструменты\beka2_v2\sheets.json', encoding='utf-8'))
ORDER = ['0','00','1.1','1.2','1.3','1.4','2.1','2.2','2.3','2.4','2.5','3.1','3.2','3.3','3.4','3.5','3.6','3.7','4.1','5.1','5.2','6.1','6.2','7.1','7.2','7.3','7.4','7.5','7.6','7.7','7.8','8.1','8.2','8.3']
M = json.load(open('w/moves.json', encoding='utf-8'))
doc = fitz.open(r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ АБК ВАРИАНТ 2.pdf')
for s in sys.argv[1:]:
    p = doc[ORDER.index(s)]; fx0, fy0, fx1, fy1 = SH[s]
    k = p.rect.width / (fx1 - fx0)
    T = lambda x, y: (( x - fx0) * k, p.rect.height - (y - fy0) * k)
    for m in M:
        if m[2] != s: continue
        a, b = T(m[5][0], m[5][3]); c, d = T(m[5][2], m[5][1])
        p.draw_rect(fitz.Rect(a, b, c, d), color=(0, 0, 1), width=1.5)
        if m[6]:
            a, b = T(m[6][0], m[6][3]); c, d = T(m[6][2], m[6][1])
            p.draw_rect(fitz.Rect(a, b, c, d), color=(1, 0, 0), width=1.5)
            cx = ((m[6][0] + m[6][2]) / 2 - fx0) * k
            p.draw_line((cx, b - 30), (cx, d), color=(1, 0, 0), width=1)
    p.get_pixmap(dpi=40).save('w/ov_%s.png' % s)
