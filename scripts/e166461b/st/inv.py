# inventory of analog wall DWGs: per frame -> texts in the stamp area (sheet no, title)
import ezdxf, json, sys, re
F = json.load(open('st/frames.json', encoding='utf-8'))
out = {}
for k in ('st1', 'st2', 'st3'):
    doc = ezdxf.readfile('st/%s.dxf' % k); msp = doc.modelspace()
    T = []
    for e in msp.query('MTEXT TEXT'):
        try:
            p = e.dxf.insert; s = e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text
        except Exception: continue
        T.append((p.x, p.y, s.replace('\n', ' ')[:140]))
    rows = []
    for fi, (x0, y0, x1, y1, sc) in enumerate(F[k]):
        inside = [t for t in T if x0 <= t[0] <= x1 and y0 <= t[1] <= y1]
        # stamp = lower-right 185 x 55 mm (scaled)
        w = x1 - x0; h = y1 - y0; s_ = w / 594.0 if w > 30000 else w / 297.0
        st = [t for t in inside if t[0] > x1 - 190 * s_ * (594.0 / 594) and t[1] < y0 + 60 * s_]
        tit = [t for t in inside if t[1] > y1 - 0.12 * h]
        rows.append(dict(i=fi, frame=[round(x0), round(y0), round(x1), round(y1)], stamp=[t[2] for t in sorted(st, key=lambda t: -t[1])], top=[t[2] for t in tit][:4]))
    out[k] = rows
    print(k, len(rows))
json.dump(out, open('st/inv.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
