"""load extdump file into records; frames <-> sheets"""
import re

FR = {  # frame handle -> sheet (from layout viewport windows)
}


class E:
    __slots__ = ('h', 'dxf', 'lay', 'bb', 'info', 'sp', 'kv')

    def __init__(s, line):
        p = line.rstrip('\n').split('|')
        s.h, s.dxf, s.lay = p[0], p[1], p[2]
        try:
            s.bb = tuple(float(v) for v in p[3:7])
        except ValueError:
            s.bb = None
        s.info = '|'.join(p[7:-1])
        s.sp = []
        for q in p[-1].split(';'):
            try: s.sp.append(tuple(float(c) for c in q.split(',')))
            except ValueError: pass
        s.kv = {}
        for part in s.info.split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                s.kv.setdefault(k, v)

    @property
    def cx(s): return (s.bb[0] + s.bb[2]) / 2

    @property
    def cy(s): return (s.bb[1] + s.bb[3]) / 2

    def txt(s): return s.kv.get('txt', '')

    def dimpts(s):
        # [p1, p2, dl] for dims
        pts = []
        for part in s.info.split(';'):
            m = re.match(r'^(-?[\d.]+),(-?[\d.]+)$', part)
            if m: pts.append((float(m.group(1)), float(m.group(2))))
        return pts

    def plpts(s):
        v = s.kv.get('pl', s.kv.get('plc', ''))
        out = []
        q = s.info.split('=', 1)[1] if s.info.startswith('pl') else ''
        for part in q.split(';'):
            a = part.split(',')
            if len(a) == 3:
                out.append((float(a[0]), float(a[1]), float(a[2])))
        return out

    def __repr__(s):
        return '%s %s %s %s %s' % (s.h, s.dxf, s.lay, tuple(round(v) for v in s.bb) if s.bb else None, s.info[:80])


def load(path):
    out = []
    for ln in open(path, encoding='utf-8-sig'):
        if ln.strip():
            out.append(E(ln))
    return out


def inside(e, w, tol=0):
    return e.bb and e.bb[0] >= w[0] - tol and e.bb[2] <= w[2] + tol and e.bb[1] >= w[1] - tol and e.bb[3] <= w[3] + tol


def touches(e, w):
    return e.bb and not (e.bb[2] < w[0] or e.bb[0] > w[2] or e.bb[3] < w[1] or e.bb[1] > w[3])
