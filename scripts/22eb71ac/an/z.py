# z.py tag page x0 y0 x1 y1 (mm, from top-left) [dpi] -> z_tag_p_n.png
import fitz, sys, os
SRC = {'F': '3. Фундамент Блок 1 Секция 1.pdf', 'S': '2.Схема каркаса Блок 1 Секция 1.pdf', 'G': '1.1 Общие данные Блок 1 Секция 1.pdf'}
D = 'D:/РАБОЧКА/Bekassyl/15_Проекты/Онкологический центр Блок 1 Секция 1/Источники/'
tag, pg = sys.argv[1], int(sys.argv[2]); x0, y0, x1, y1 = map(float, sys.argv[3:7]); dpi = int(sys.argv[7]) if len(sys.argv) > 7 else 220
k = 72 / 25.4
p = fitz.open(D + SRC[tag])[pg - 1]
out = 'z_%s%d_%d_%d.png' % (tag, pg, x0, y0)
p.get_pixmap(dpi=dpi, clip=fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k)).save(out); print(out)
