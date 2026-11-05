"""finish a retiled plan sheet: axis labels, new frame format, stamp/table to the new frame corner, plan offset"""
import ext, ab, plan, sheets, re

LET = ['А', 'Б', 'В', 'Г', 'Д', 'Е']
FMT = {  # name -> (Format, Multiplicity, width, height) in mm
    'A3x3': ('A3', 3, 891, 420), 'A3': ('A3', 1, 297, 420), 'A2': ('A2', 1, 594, 420), 'A4x3': ('A4', 3, 630, 297),
    'A2x3': ('A2', 3, 1261, 594), 'A3x4': ('A3', 4, 1189, 420), 'A1': ('A1', 1, 841, 594)}


def clean(s):
    return re.sub(r'\\[A-Za-z][^;]*;|[{}]', '', s)


def axes_labels(es, nums=True, lets=True, win=None):
    ops = []
    vals = plan.axis_vals(win) if win else {}
    okv = lambda v: v.isdigit() or (0 < len(v) <= 2 and '.' not in v)
    ax = [e for e in es if e.dxf == 'SPDSCONSTRUCTIONLINE' and len(e.sp) >= 2 and (not vals or okv(vals.get(e.h, ''))) and abs(e.sp[0][0] - e.sp[1][0]) + abs(e.sp[0][1] - e.sp[1][1]) > 9000]
    vert = [e for e in ax if abs(e.sp[0][0] - e.sp[1][0]) < 1]
    hor = [e for e in ax if abs(e.sp[0][1] - e.sp[1][1]) < 1]
    if nums:
        xs = sorted(set(round(e.sp[0][0]) for e in vert))
        for e in vert:
            ops.append({'t': 'axisval', 'h': e.h, 'val': str(xs.index(round(e.sp[0][0])) + 1)})
    if lets:
        ys = sorted(set(round(e.sp[0][1]) for e in hor))
        for e in hor:
            ops.append({'t': 'axisval', 'h': e.h, 'val': LET[ys.index(round(e.sp[0][1]))]})
    return ops


def stamp_group(es, frame):
    """stamp insert + everything inside its box + tables + table titles + sheet-number text"""
    sb = plan.stamp_box(es)
    grp = []
    tabs = [e for e in es if e.dxf == 'ACAD_TABLE' and ext.inside(e, frame, 1)]
    for e in es:
        if not ext.inside(e, frame, 1) or e.dxf == 'SPDSFORMAT': continue
        if sb and ext.inside(e, sb, 1): grp.append(e); continue
        if e in tabs: grp.append(e); continue
        if e.dxf in ('MTEXT', 'TEXT'):
            t = clean(e.txt())
            for tb in tabs:
                if tb.bb[0] - 200 <= e.cx <= tb.bb[2] + 200 and tb.bb[3] - 100 <= e.bb[1] <= tb.bb[3] + 2500 and ('Специф' in t or 'Ведомость' in t or 'Таблица' in t):
                    grp.append(e); break
    return grp


def finish(sheet, fmt, plan_d, win_extra=80000, labels=(True, True), extra_stamp=()):
    sx, sy = sheets.slot(sheet)
    win = (sx - 100, sy - 100, sx + win_extra + 10000, sy + 60000)
    es = plan.dump(win, 'fin_' + sheet.replace('.', ''))
    fr = [e for e in es if e.dxf == 'SPDSFORMAT']
    fr = min(fr, key=lambda f: abs(f.bb[0] - sx) + abs(f.bb[1] - sy))
    frame = fr.bb
    F, mul, wmm, hmm = FMT[fmt]
    sc = 100.0 if (frame[2] - frame[0]) > 20000 * 1.0 and abs((frame[2] - frame[0]) / 297 - 100) < 1 or True else 100.0
    sc = round((frame[3] - frame[1]) / 420.0) if abs((frame[3] - frame[1]) / 420.0 - round((frame[3] - frame[1]) / 420.0)) < 0.01 else round((frame[2] - frame[0]) / 297.0)
    grp = stamp_group(es, frame) + [e for e in es if e.h in extra_stamp]
    gh = set(e.h for e in grp)
    body = [e for e in es if e.h not in gh and e.h != fr.h and e.bb and e.bb[0] >= frame[0] - 100 and e.bb[1] >= frame[1] - 100]
    neww = wmm * sc; newh = hmm * sc
    dxs = (frame[0] + neww) - frame[2]
    dys = 0.0
    ops = [{'t': 'mcset', 'h': fr.h, 'set': {'Format': F, 'Multiplicity': mul}}, {'t': 'mcset', 'h': fr.h, 'set': {'Horizontal': wmm > hmm}}]
    if grp: ops.append({'t': 'move', 'h': [e.h for e in grp], 'd': [dxs, dys]})
    if plan_d != (0, 0): ops.append({'t': 'move', 'h': [e.h for e in body], 'd': list(plan_d)})
    ops += axes_labels(body, labels[0], labels[1], win)
    ops.append({'t': 'save'})
    out = ab.run(ops, 'fin_' + sheet.replace('.', ''))
    print(out[-400:])
    return (frame[0], frame[1], frame[0] + neww, frame[1] + newh)
