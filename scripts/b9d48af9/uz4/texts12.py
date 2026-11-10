# Dump TEXT/MTEXT (and line/polyline counts) of DWG sheets 1-4 as JSON: sheet, x, y (mm on paper from the sheet's lower-left, 1:100), height, width, rotation, text.
import sys, json, ezdxf
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
sheets = {1: (804165 - 42000, 804165), 2: (846165 - 42000, 846165), 3: (888165 - 42000, 888165), 4: (917865 - 29700, 917865)}
y0 = -274400; out = []
for e in msp.query('TEXT MTEXT'):
    p = e.dxf.insert
    for n, (xa, xb) in sheets.items():
        if xa - 50 <= p.x <= xb + 50 and y0 - 100 <= p.y <= y0 + 42100:
            if e.dxftype() == 'TEXT':
                t = e.dxf.text; h = e.dxf.height; w = 0; att = 7
                hal = e.dxf.get('halign', 0); val = e.dxf.get('valign', 0)
                if hal or val: p = e.dxf.get('align_point', p)
                att = {(0, 0): 7, (1, 0): 8, (2, 0): 9}.get((hal, val), 7)
            else:
                t = e.plain_text(); h = e.dxf.char_height; w = e.dxf.get('width', 0); att = e.dxf.get('attachment_point', 1)
            out.append(dict(s=n, x=round((p.x - xa) / 100, 2), y=round((p.y - y0) / 100, 2), h=round(h / 100, 2), w=round(w / 100, 1), r=round(e.dxf.get('rotation', 0), 1), a=att, kind=e.dxftype(), t=t, layer=e.dxf.layer))
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for n in sheets: print(n, sum(1 for o in out if o['s'] == n))
