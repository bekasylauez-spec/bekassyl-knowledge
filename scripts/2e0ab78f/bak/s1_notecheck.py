# -*- coding: utf-8 -*-
"""Выноска тексерісі (ЕРЕЖЕЛЕР №119): notelist + geomdump геометриясынан kzh_note_rule.check(); Arrow саны."""
import s1_lib as L, s1_ab, json, glob, os, math, sys, collections
S = r'D:\_claude_work\otst\s1'
X1 = max(L.SHEETX.values()) + 59400
gf = os.path.join(S, 'job', 'geom_n.txt')
r = s1_ab.run([dict(t='notelist'), dict(t='geomdump', win=[-100, 599900, X1 + 100, 642100], file=gf)], 'ncheck', 1200)
log = s1_ab.log()
segs = collections.defaultdict(list)
for l in open(gf, encoding='utf-8-sig'):
    p = l.strip().split('|')
    if p[0] == 'S' and p[2] == 'SPDSNOTEPOSITION': segs[p[1]].append(tuple(map(float, p[3:7])))
exp = {}
for f in glob.glob(os.path.join(S, 'job', 'notes_*.json')):
    for n in json.load(open(f, encoding='utf-8')): exp[(round(n['target'][0] / 5), round(n['target'][1] / 5), n['l1'])] = n
def sheet_of(x):
    for n in L.SLOTS:
        w = 42000 if n == '1.2' else 59400
        if L.SHEETX[n] <= x <= L.SHEETX[n] + w: return n
    return '?'
notes = []; arrows = collections.Counter(); per = collections.Counter()
for l in log.splitlines():
    p = l.split('\t')
    if p[0] != 'N' or p[2] != 'SPDSNOTEPOSITION': continue
    h, l1, arrow = p[1], p[3], p[8]
    pts = [tuple(map(float, q.split(','))) for q in p[9:] if not q.startswith('E') and ',' in q]
    if not pts: continue
    o = pts[0]
    if not (599900 <= o[1] <= 642100 and -100 <= o[0] <= X1): continue
    sh = sheet_of(o[0]); arrows[arrow] += 1; per[sh] += 1
    # геометрия: полка — origin-нен басталатын горизонталь кесінді; выноска сызығы — origin-ге тиетін қиғаш кесінді
    shelf_end = None; target = None
    for (x1, y1, x2, y2) in segs.get(h, []):
        for (ax, ay, bx, by) in ((x1, y1, x2, y2), (x2, y2, x1, y1)):
            if math.hypot(ax - o[0], ay - o[1]) < 3:
                if abs(by - ay) < 1 and abs(bx - ax) > 50: shelf_end = (bx, by)
                elif math.hypot(bx - ax, by - ay) > 50: target = (bx, by)
    if target is None or shelf_end is None:
        notes.append(dict(id='%s %s [%s]' % (sh, h, l1), bad='геометрия оқылмады (target %s, shelf %s)' % (target, shelf_end))); continue
    e = exp.get((round(target[0] / 5), round(target[1] / 5), l1))
    notes.append(dict(id='%s %s [%s] @(%d,%d)' % (sh, h, l1, o[0] - L.SHEETX.get(sh, 0), o[1] - L.ROW_Y), target=target, origin=o, shelf_end=shelf_end, arrow=arrow,
                      ends_on=(e['ends_on'] if e else 'line'), kind='pos'))
bad = [(n['id'], n['bad']) for n in notes if 'bad' in n] + L.KNR.check([n for n in notes if 'bad' not in n])
for b in bad: print('BAD', b)
print('NOTES', len(notes), dict(per))
print('ARROW түрлері', dict(arrows))
print('BAD', len(bad))
