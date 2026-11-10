# ACAD_TABLE / block inserts on DWG sheet 2: explode to lines + texts (paper mm, 1:100) appended to lines12.json / texts12.json
import sys, json, ezdxf
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
xa = 846165 - 42000; y0 = -274400
L = json.load(open(sys.argv[2], encoding='utf-8')); T = json.load(open(sys.argv[3], encoding='utf-8'))
cnt = 0
for e in msp:
    if e.dxftype() != 'ACAD_TABLE': continue
    try: p = e.dxf.insert
    except Exception: continue
    if not (xa <= p.x <= xa + 42000 and y0 <= p.y <= y0 + 29700): continue
    try: ve = list(e.virtual_entities())
    except Exception as ex: print('noexplode', e.dxftype(), ex); continue
    print(e.dxftype(), getattr(e.dxf, 'name', ''), len(ve))
    for v in ve:
        t = v.dxftype()
        if t == 'LINE':
            a = ((v.dxf.start.x - xa) / 100, (v.dxf.start.y - y0) / 100); b = ((v.dxf.end.x - xa) / 100, (v.dxf.end.y - y0) / 100)
            if min(a[0], b[0]) > 234 and max(a[1], b[1]) < 57: continue
            L.append(dict(s=2, a=[round(a[0], 2), round(a[1], 2)], b=[round(b[0], 2), round(b[1], 2)], lw=-1)); cnt += 1
        elif t in ('TEXT', 'MTEXT'):
            q = v.dxf.insert; txt = v.dxf.text if t == 'TEXT' else v.plain_text(); h = v.dxf.height if t == 'TEXT' else v.dxf.char_height
            x = (q.x - xa) / 100; y = (q.y - y0) / 100
            if x > 234 and y < 57: continue
            att = 7
            if t == 'TEXT':
                hal = v.dxf.get('halign', 0); val = v.dxf.get('valign', 0)
                if hal or val: q2 = v.dxf.get('align_point', q); x = (q2.x - xa) / 100; y = (q2.y - y0) / 100
                att = {0: 7, 1: 8, 2: 9, 4: 8}.get(hal, 7) if val in (0, 1) else {0: 4, 1: 5, 2: 6}.get(hal, 4)
            else: att = v.dxf.get('attachment_point', 1)
            T.append(dict(s=2, x=round(x, 2), y=round(y, 2), h=round(h / 100, 2), w=round(v.dxf.get('width', 0) / 100, 1) if t == 'MTEXT' else 0, r=0, a=att, kind=t, t=txt, layer='table')); cnt += 1
json.dump(L, open(sys.argv[2], 'w', encoding='utf-8'), indent=0); json.dump(T, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('added', cnt)
