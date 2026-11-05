# oc.py <dxf> <sheets.json> [only]  — проверка оформления: текст на тексте, линия через текст (по геометрии DXF)
# Тексты: MTEXT, TEXT, тексты размеров (virtual entities), тексты СПДС-прокси (proxy graphics).
# Линии: LINE/LWPOLYLINE, линии размеров, линии прокси (выноски, отметки, оси, разрезы). Свои линии родителя не считаются.
import sys, json, math
import ezdxf
from ezdxf.proxygraphic import ProxyGraphic
from shapely.geometry import Polygon, LineString, box
from shapely import affinity

doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
sheets = json.load(open(sys.argv[2], encoding='utf-8'))
args = [a for a in sys.argv[3:] if not a.startswith('--geom=')]
only = args[0] if args else None
GEOM = next((a[7:] for a in sys.argv[3:] if a.startswith('--geom=')), None)   # SPDS geometry exploded by AutoCAD (rz.cs geomdump)
unread = []                                                                      # entities whose geometry could not be read: never skip silently
CW = 0.72                                                   # ISOCPEUR letters: width / height (measured)
def TW(t): return sum(0.85 if ch.isdigit() else CW for ch in t)   # digits are wider (0.85 h, measured 31.10)

def tbox(x, y, h, rot, s, halign=0, valign=0):
    w = max(TW(s), CW) * h
    x0 = {0: 0, 1: -w / 2, 2: -w}.get(halign, 0); y0 = {0: 0, 1: 0, 2: -h / 2, 3: -h}.get(valign, 0)
    p = box(x + x0, y + y0, x + x0 + w, y + y0 + h)
    return affinity.rotate(p, rot, origin=(x, y))

def mtext_box(e, ox=0, oy=0):
    txt = e.plain_text().split('\n'); h = e.dxf.char_height
    w = max(TW(t) for t in txt) * h; H = len(txt) * h * 1.6
    if e.dxf.hasattr('width') and e.dxf.width > 0 and w > e.dxf.width * 1.02:      # MTEXT wraps at its width
        W0 = e.dxf.width; n = sum(max(1, math.ceil(TW(t) * h / W0)) for t in txt)
        w = W0; H = n * h * 1.6
    ap = e.dxf.get('attachment_point', 1)
    ix, iy = e.dxf.insert[0], e.dxf.insert[1]
    dx = {1: 0, 2: -w / 2, 3: -w}[(ap - 1) % 3 + 1]; dy = {0: -H, 1: -H / 2, 2: 0}[(ap - 1) // 3]
    p = box(ix + dx, iy + dy, ix + dx + w, iy + dy + H)
    rot = e.dxf.get('rotation', 0)
    if e.dxf.hasattr('text_direction'):
        d = e.dxf.text_direction; rot = math.degrees(math.atan2(d[1], d[0]))
    return affinity.rotate(p, rot, origin=(ix, iy)), '|'.join(txt)

texts, segs = [], []
class _Segs(list):
    def append(self, it):
        c = it[1].coords
        if any(abs(x) < 1 and abs(y) < 1 for x, y in c) or it[1].length > 30000: return   # proxy-graphic artefacts
        list.append(self, it)
segs = _Segs()                                        # (parent, poly, label) / (parent, LineString)
def add_geo(pid, ents):
    for v in ents:
        t = v.dxftype()
        if t == 'LINE': segs.append((pid, LineString([(v.dxf.start.x, v.dxf.start.y), (v.dxf.end.x, v.dxf.end.y)])))
        elif t in ('LWPOLYLINE', 'POLYLINE'):
            pts = [(float(p[0]), float(p[1])) for p in (v.get_points('xy') if t == 'LWPOLYLINE' else [q.dxf.location for q in v.vertices])]
            if v.closed if t == 'LWPOLYLINE' else v.is_closed: pts = pts + pts[:1]
            for a, b in zip(pts, pts[1:]): segs.append((pid, LineString([a, b])))
        elif t == 'TEXT':
            s = v.dxf.text.strip()
            if s: texts.append((pid, tbox(v.dxf.insert[0], v.dxf.insert[1], v.dxf.height, v.dxf.get('rotation', 0), s,
                                          v.dxf.get('halign', 0), v.dxf.get('valign', 0)), s))
        elif t == 'MTEXT':
            p, s = mtext_box(v)
            if s.strip(): texts.append((pid, p, s))

ptype = {}
NOPLOT_L = set()
for _l in doc.layers:
    try:
        if _l.dxf.get('plot', 1) == 0 or _l.is_off() or _l.is_frozen(): NOPLOT_L.add(_l.dxf.name)
    except Exception: pass
NOPLOT = set()
for e in msp:
    try:
        if e.dxf.layer in NOPLOT_L: NOPLOT.add(e.dxf.handle)
    except Exception: pass
import os as _os
_np = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'noplot.txt')
if _os.path.exists(_np): NOPLOT |= set(open(_np).read().split())
for e in msp:
    if e.dxf.handle in NOPLOT: continue
    t = e.dxftype(); pid = e.dxf.handle; ptype[pid] = t
    if t in ('HATCH', 'INSERT', 'CIRCLE', 'ARC', 'ACAD_TABLE', 'POINT'): continue
    try: lay = e.dxf.layer
    except Exception: lay = ''
    if lay in ('О_Формат', 'Формат - тонкая линия', 'Формат - толстая линия', 'Штамп', 'Рамка_Штамп'): continue
    try:
        if t == 'DIMENSION':
            if GEOM: continue                                  # dims from the AutoCAD dump (moved texts placed exactly)
            add_geo(pid, list(e.virtual_entities()))
        elif t == 'ACAD_PROXY_ENTITY' or t.startswith('SPDS'):
            if t == 'SPDSFORMAT': continue
            if GEOM: continue                                  # taken from the AutoCAD dump below
            if not getattr(e, 'proxy_graphic', None): continue
            ve = list(ProxyGraphic(e.proxy_graphic, doc).virtual_entities())
            if any(v.dxftype() == 'LINE' and v.dxf.start.distance(v.dxf.end) > 20000 for v in ve): continue   # format frames
            add_geo(pid, ve)
        else: add_geo(pid, [e])
    except Exception as ex:
        unread.append((pid, t, str(ex)[:60]))
if GEOM:
    from shapely.geometry import box as _box
    GS, GT = {}, {}
    for ln in open(GEOM, encoding='utf-8-sig'):
        f = ln.rstrip('\r\n').split('|')
        if len(f) > 1 and f[1] in NOPLOT: continue
        if f[0] == 'S':
            ptype[f[1]] = f[2]; a_, b_ = (float(f[3]), float(f[4])), (float(f[5]), float(f[6]))
            if a_ != b_: GS.setdefault(f[1], []).append((a_, b_))
        elif f[0] == 'T' and f[7].strip():
            ptype[f[1]] = f[2]; GT.setdefault(f[1], []).append(([float(v) for v in f[3:7]], f[7].strip()))
    # SPDS callouts: Explode returns the text unmirrored (Angle = pi ignored), but each text has its own frame
    # (unplotted mask rectangle) at the real place -> the text box is taken from the frame, the frame lines are dropped
    for pid_ in set(GS) | set(GT):
        sg = GS.get(pid_, []); used = set()
        hs = [i for i, (a_, b_) in enumerate(sg) if abs(a_[1] - b_[1]) < 0.5]
        vs = [i for i, (a_, b_) in enumerate(sg) if abs(a_[0] - b_[0]) < 0.5]
        rects = []
        for i in hs:
            for j in hs:
                if j <= i: continue
                (a1, b1), (a2, b2) = sg[i], sg[j]
                x0, x1 = sorted([a1[0], b1[0]]); u0, u1 = sorted([a2[0], b2[0]])
                if abs(x0 - u0) > 1 or abs(x1 - u1) > 1 or abs(a1[1] - a2[1]) < 1: continue
                y0, y1 = sorted([a1[1], a2[1]])
                side = [k for k in vs if min(abs(sg[k][0][0] - x0), abs(sg[k][0][0] - x1)) < 1 and
                        abs(min(sg[k][0][1], sg[k][1][1]) - y0) < 1 and abs(max(sg[k][0][1], sg[k][1][1]) - y1) < 1]
                if len(side) >= 2: rects.append(((x0, y0, x1, y1), {i, j, side[0], side[1]}))
        for bb, txt in GT.get(pid_, []):
            w, h = bb[2] - bb[0], bb[3] - bb[1]; fit = None
            best_ = None
            for (x0, y0, x1, y1), ids in rects:
                if abs((x1 - x0) - w) < 0.35 * w + 150 and abs((y1 - y0) - h) < h and not (ids & used):
                    sc_ = abs((x1 - x0) - w) + abs((y1 - y0) - h)     # best-fitting frame, not the first (knot ellipse box is also a rectangle)
                    if best_ is None or sc_ < best_[0]: best_ = (sc_, ((x0, y0, x1, y1), ids))
            if best_: fit = best_[1]
            if fit:
                used |= fit[1]; m = 0.4 * ((fit[0][3] - fit[0][1]) - h)
                texts.append((pid_, _box(fit[0][0] + m, fit[0][1] + m, fit[0][2] - m, fit[0][3] - m), txt))
            else:
                texts.append((pid_, _box(*bb), txt))
        for k, (a_, b_) in enumerate(sg):
            if k not in used: segs.append((pid_, LineString([a_, b_])))

import re
LEV = re.compile(r'^[+\-−]?\d+[.,]\d{3}$')
ptexts = {}
for pid_, poly_, s_ in texts: ptexts.setdefault(pid_, []).append(s_)
notes_ = {pid_ for pid_, ts in ptexts.items() if any(len(t) >= 3 and not LEV.match(t) for t in ts)}
tb = {}
for pid_, poly_, s_ in texts: tb.setdefault(pid_, []).append(poly_.bounds)
def _is_shelf(pid_, ls_):
    (xa, ya), (xb, yb) = ls_.coords[0], ls_.coords[-1]
    if abs(ya - yb) > 1 or ls_.length < 50: return False
    for (bx0, by0, bx1, by1) in tb.get(pid_, []):
        hh = by1 - by0
        if min(max(xa, xb), bx1) - max(min(xa, xb), bx0) > 0.5 * (bx1 - bx0) and (abs(ya - by0) < 0.8 * hh or abs(ya - by1) < 0.8 * hh): return True
    return False
shelves = [(pid_, ls_) for pid_, ls_ in segs if ptype.get(pid_, '').startswith('SPDSNOTE') and _is_shelf(pid_, ls_)]   # SPDS callouts only
strokes = [(pid_, ls_) for pid_, ls_ in segs if ptype.get(pid_) in ('SPDSSECTION', 'SPDSCONSTRUCTIONLINE') and ls_.length <= 1000]   # section mark strokes/arrows
hatches = []                                                      # concrete/ground hatch areas: no text on them
for e in msp.query('HATCH'):
    try:
        acc = None                                                   # even-odd: outer boundary minus holes
        for path in e.paths:
            pts = []
            if hasattr(path, 'vertices') and path.vertices: pts = [(float(v[0]), float(v[1])) for v in path.vertices]
            elif hasattr(path, 'edges'):
                for ed in path.edges:
                    if hasattr(ed, 'start'): pts.append((float(ed.start[0]), float(ed.start[1])))
            if len(pts) >= 3:
                pg = Polygon(pts).buffer(0)
                if pg.area > 0: acc = pg if acc is None else acc.symmetric_difference(pg)
        if acc is not None and acc.area > 0: hatches.append((e.dxf.handle, acc))
    except Exception as ex:
        unread.append((e.dxf.handle, 'HATCH', str(ex)[:40]))
total = 0
for name, (x0, y0, x1, y1) in sheets.items():
    if only and name != only: continue
    W = box(x0, y0, x1, y1)
    T = [(p, poly, s) for p, poly, s in texts if W.contains(poly.centroid)]
    L = [(p, ls) for p, ls in segs if W.intersects(ls)]
    found = []
    for i in range(len(T)):
        pi_, a, sa = T[i]; ash = a.buffer(-0.12 * math.sqrt(a.area / max(len(sa), 1)))
        for j in range(i + 1, len(T)):
            pj, b, sb = T[j]
            if pi_ == pj: continue
            if ash.intersects(b) and ash.intersection(b).area > 0.005 * min(a.area, b.area):   # any real touch
                found.append(('ТЕКСТ/ТЕКСТ', sa+'#'+pi_, sb+'#'+pj, a.centroid))
        for pl, ls in L:
            if pl == pi_: continue
            if ash.intersects(ls) and ash.intersection(ls).length > 0.03 * math.sqrt(a.area / max(len(sa), 1)):
                found.append(('ЛИНИЯ/ТЕКСТ', sa+'#'+pi_, pl, a.centroid))
    # a note shelf must not run across an axis, an element or another line (Bekassyl 31.10, sheet 3.2)
    for ps, sh in shelves:
        if not W.intersects(sh): continue
        for pl, ls in L:
            if pl == ps or (ptype.get(pl) == 'SPDSCONSTRUCTIONLINE' and ls.length > 1000): continue   # invisible middle of a cut line
            if ptype.get(pl) == 'DIMENSION' and sh.intersection(ls).geom_type == 'LineString' and sh.intersection(ls).length > 1: continue  # «1/ш.200 →» continuing a chain (analog 3.2)
            if sh.crosses(ls) or (sh.intersects(ls) and sh.intersection(ls).length > 1):
                txt = '|'.join(ptexts.get(ps, []))
                found.append(('ПОЛКА/ЛИНИЯ', txt, pl, sh.centroid))
    for ps, st in strokes:
        if not W.intersects(st): continue
        for pl, ls in L:
            if pl == ps or (ptype.get(pl) in ('SPDSCONSTRUCTIONLINE', 'SPDSSECTION') and ls.length > 1000): continue
            if ptype.get(ps) == 'SPDSCONSTRUCTIONLINE' and ptype.get(pl) == 'DIMENSION': continue   # an axis may pass through dims
            if st.crosses(ls) or (st.intersects(ls) and st.intersection(ls).length > 1):
                found.append(('ЗНАК РАЗРЕЗА/ЛИНИЯ', '|'.join(ptexts.get(ps, []))+'#'+ps, pl, st.centroid))
    # every text inside the inner frame (20 mm left, 5 mm elsewhere) and off the stamp (185 x 55 mm, bottom right)
    SC = {'2.3': 50, '3.7': 25, '1.3': 100, '1.3x': 100, '2.1': 100, '2.2': 100, '2.3': 100, '2.4': 100, '2.5': 100, '3.1': 100, '3.2': 100, '2.6': 100, '2.7': 100, '4.1': 50, '4.2': 50, '4.3': 50, '4.4': 50, '4.5': 50, '4.6': 50}.get(name, max(1, round((x1 - x0) / 594))); m5, m20 = 5 * SC, 20 * SC
    inner = box(x0 + m20, y0 + m5, x1 - m5, y1 - m5); stamp = box(x1 - m5 - 185 * SC, y0 + m5, x1 - m5, y0 + m5 + 55 * SC)
    for p_, poly, s_ in T:
        if ptype.get(p_, '') in ('SPDSFORMAT',): continue
        if not inner.contains(poly): found.append(('ЗА РАМКОЙ', s_, '', poly.centroid))
        elif poly.intersects(stamp) and not stamp.contains(poly): found.append(('НА ШТАМПЕ', s_, '', poly.centroid))
    for p_, poly, s_ in T:
        for hh_, hg in hatches:
            if hg.intersects(poly) and hg.intersection(poly).area > 0.15 * poly.area:
                found.append(('ТЕКСТ НА ШТРИХОВКЕ', s_, hh_, poly.centroid)); break
    total += len(found)
    print('==', name, len(found))
    seen = set()
    for k, sa, sb, c in found:
        key = (k, sa, str(sb), round(c.x / 200), round(c.y / 200))
        if key in seen: continue
        seen.add(key)
        print('  %s  "%s"  <> %s  @(%.0f, %.0f)' % (k, sa, sb, c.x - x0, c.y - y0))
if unread:
    print('НЕ ПРОЧИТАНО (проверка неполная!):', len(unread), sorted({u[1] for u in unread}))
    total += len(unread)
print('TOTAL', total)
