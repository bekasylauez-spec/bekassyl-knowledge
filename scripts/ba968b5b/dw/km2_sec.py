# -*- coding: utf-8 -*-
"""Км-2 (400×800, 12Ø28): 4.2 парағындағы разрезді 400 → 800 созу (көшірілген Км-1 разрезінен).
Масштаб разрезде: 1 мм = 2 бірлік. Ұзын жағы — көлденең (Ц.0 осі бойымен)."""
import ab, os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
LOG = os.path.join(os.environ['TEMP'], 'ab_log.txt')
def listwin(w):
    ab.run([{'t': 'list', 'win': w}], 'lsw', 300)
    out = []
    for l in open(LOG, encoding='utf-8-sig'):
        p = l.rstrip('\n').split('\t')
        if p[0] == 'L':
            x0, y0, x1, y1 = map(float, p[4][1:].split(','))
            pts = [tuple(map(float, q.split(','))) for q in p[5:] if q]
            out.append(dict(t=p[1], h=p[2], lay=p[3], e=(x0, y0, x1, y1), pts=pts))
    return out

def widen(xc, ybot, ytop, hoops_outer, hoops_diamond, mid_bars, half=400, extra_inner=True):
    """xc — разрез ортасы (Б.0 осі), ybot..ytop — разрездің тік ауқымы (атаудан төмен)."""
    W = 2200
    ops = [{'t': 'stretchwin', 'win': [xc + 10, ybot, xc + W, ytop], 'd': [half, 0]},
           {'t': 'stretchwin', 'win': [xc - W, ybot, xc - 10, ytop], 'd': [-half, 0]}]
    print(ab.run(ops, 'sw', 300)[-200:])
    # хомут блоктары stretchwin-мен тұтас жылжыған болса — орнына қайтарып, X бойынша созамыз
    ents = {e['h']: e for e in listwin([xc - W, ybot, xc + W, ytop])}
    fix = []
    for h, wnew in hoops_outer + hoops_diamond:
        e = ents[h]; cx = (e['e'][0] + e['e'][2]) / 2
        if abs(cx - xc) > 50: fix.append({'t': 'move', 'h': [h], 'd': [xc - cx, 0]})
    if fix: print(ab.run(fix, 'fix', 300)[-120:])
    ents = {e['h']: e for e in listwin([xc - W, ybot, xc + W, ytop])}
    ops = []
    for h, wnew in hoops_outer + hoops_diamond:
        e = ents[h]; w0 = e['e'][2] - e['e'][0]
        ops.append({'t': 'xscale', 'h': [h], 'sx': (w0 + 2 * half) / w0, 'bx': xc})
    print(ab.run(ops, 'xs', 300)[-300:])
    # жаңа стерженьдер ±360 бірлік (±180 мм): ұзын қырлардың ортаңғы стерженьдерінен
    ops = []
    for h in mid_bars:
        for dx in (-half * 0.9, half * 0.9):
            ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    print(ab.run(ops, 'bars', 300)[-300:])
    return

def split_dims(xc, ybot, ytop, half=400):
    """160 мм размерлері созылып 360 мм болды → 180|180 етіп бөлу (бір шеті xc-де)."""
    ents = listwin([xc - 2400, ybot - 2000, xc + 2400, ytop])
    ops = []
    for e in ents:
        if e['t'] != 'DIMENSION' or len(e['pts']) < 4: continue
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = e['pts'][:4]
        # көлденең размер: XLine1/XLine2 = pts[0], pts[1]
        if abs(y1 - y2) > 60: continue
        L = abs(x2 - x1)
        if abs(L - 2 * half * 0.9) < 15 and (abs(x1 - xc) < 5 or abs(x2 - xc) < 5):
            far = x1 if abs(x2 - xc) < 5 else x2; s = 1 if far > xc else -1
            mid = xc + s * half * 0.9
            ops.append({'t': 'dimpts', 'h': e['h'], 'p1': [far, y1], 'p2': [mid, y1]})
            ops.append({'t': 'clone', 'h': e['h'], 'base': [0, 0], 'to': [0, 0], 'tag': 'dimclone_%s' % e['h']})
            print('split', e['h'], round(x1), round(x2))
    print(ab.run(ops, 'sd', 300)[-400:])
    return ops

if __name__ == '__main__':
    pass
