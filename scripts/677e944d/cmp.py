import fitz, os
from PIL import Image
def pg(path, i, dpi, clip=None):
    d = fitz.open(path); p = d[i]; r = p.rect
    c = fitz.Rect(r.width * clip[0], r.height * clip[1], r.width * clip[2], r.height * clip[3]) if clip else None
    pm = p.get_pixmap(dpi=dpi, clip=c); return Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
O = r'D:\_claude_work\otst\out'
ours = r'D:\РАБОЧКА\От Маке\Завод\Отстойник\КЖ Вторичный отстойник.pdf'
out = os.path.join(os.path.dirname(__file__), 'ot')
for k, (a, i) in enumerate([('an07', 9), ('an08', 10), ('an11', 15), ('an12', 16)]):
    A = pg(os.path.join(O, a + '.pdf'), 0, 60); B = pg(ours, i, 60)
    B = B.resize((int(B.width * A.height / B.height), A.height))
    S = Image.new('RGB', (A.width + B.width + 20, A.height), 'red'); S.paste(A, (0, 0)); S.paste(B, (A.width + 20, 0)); S.save(os.path.join(out, 'cmp%d.png' % k)); print(a, A.size, B.size)
