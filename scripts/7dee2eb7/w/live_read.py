# Read (no edits) the user's open Б4.плита1.dwg in their AutoCAD: entities around the openings on every Пм1 sheet.
import json, time
import pywintypes
def R(f, n=600):
    for _ in range(n):
        try: return f()
        except pywintypes.com_error as ex:
            if ex.args[0] in (-2147418111, -2147417846): time.sleep(0.5); continue
            raise
    return f()
import pythoncom, win32com.client
from win32com.client import VARIANT

acad = win32com.client.GetActiveObject('AutoCAD.Application')
doc = None
docs = R(lambda: acad.Documents)
for j in range(R(lambda: docs.Count)):
    d = R(lambda: docs.Item(j)); nm = R(lambda: d.Name)
    if nm.lower().startswith('б4.плита1') and 'v2' not in nm.lower(): doc = d
print('doc', R(lambda: doc.Name), 'saved?', R(lambda: doc.Saved))
OPEN = {'O1': (26725, 1700, 29275, 7300), 'O2': (39950, 17050, 44550, 25950), 'ST': (12950, 36250, 18650, 39300)}
SHEETS = [(-791072 + i * 90000 + 9000, -3120000 - 51000) for i in range(6)]
ss_name = 'p4_live_read'
try: R(lambda: doc.SelectionSets.Item(ss_name).Delete())
except Exception: pass
ss = R(lambda: doc.SelectionSets.Add(ss_name))
ft = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, [0])
fd = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, ['LWPOLYLINE,LINE,POLYLINE'])
R(lambda: ss.Select(5, None, None, ft, fd))
N = R(lambda: ss.Count); print('count', N)
out = []
boxes = []
for si, (ox, oy) in enumerate(SHEETS):
    for k, (a, b, c, d) in OPEN.items():
        boxes.append((si, k, ox + a - 60, oy + b - 60, ox + c + 60, oy + d + 60, ox, oy))
for i in range(N):
    e = R(lambda: ss.Item(i))
    try:
        on = R(lambda: e.ObjectName)
        if on == 'AcDbLine':
            p = list(R(lambda: e.StartPoint))[:2] + list(R(lambda: e.EndPoint))[:2]; pts = [(p[0], p[1]), (p[2], p[3])]
        else:
            c = list(R(lambda: e.Coordinates)); st = 2 if on == 'AcDbPolyline' else 3
            pts = [(c[j], c[j + 1]) for j in range(0, len(c), st)]
    except Exception: continue
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    for (si, k, x0, y0, x1, y1, ox, oy) in boxes:
        if min(xs) >= x0 and max(xs) <= x1 and min(ys) >= y0 and max(ys) <= y1:
            out.append(dict(sheet=si, op=k, type=on, h=R(lambda: e.Handle), layer=R(lambda: e.Layer), lw=R(lambda: e.Lineweight), color=R(lambda: e.Color),
                            pts=[(round(q[0] - ox, 1), round(q[1] - oy, 1)) for q in pts]))
R(lambda: ss.Delete())
json.dump(out, open('live_open.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for o in out: print(o['sheet'], o['op'], o['type'], o['h'], o['layer'], o['lw'], o['color'], o['pts'][:5])
