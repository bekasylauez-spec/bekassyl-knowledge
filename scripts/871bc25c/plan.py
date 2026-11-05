"""plan-sheet pipeline helpers"""
import ext, ab, retile, sheets, os

W = ab.S + r'\w'


def dump(win, name):
    f = os.path.join(W, name + '.txt')
    out = ab.run([{'t': 'extdump', 'file': f, 'win': list(win)}], 'dump_' + name)
    if 'extdump ok' not in out: raise RuntimeError(out)
    return ext.load(f)


def stamp_box(es):
    st = [e for e in es if e.dxf == 'INSERT' and e.kv.get('blk') == 'крпкер']
    if not st: return None
    b = st[0].bb
    return (b[0] - 10, b[1] - 10, b[2] + 10, b[3] + 10)


def work_set(es, win, extra_excl=()):
    sb = stamp_box(es)
    out = []
    for e in es:
        if not ext.inside(e, win, 1): continue
        if e.dxf in ('SPDSFORMAT', 'ACAD_TABLE'): continue
        if sb and ext.inside(e, sb, 1): continue
        if any(ext.inside(e, b, 1) for b in extra_excl): continue
        out.append(e)
    return out


def run_pass(es, ps, pre, name, chunk=1500):
    ops, erase, st = retile.plan_pass(es, ps, pre)
    print(name, st, 'ops', len(ops), 'erase', len(erase))
    res = ''
    for i in range(0, len(ops), chunk):
        res += ab.run(ops[i:i + chunk], '%s_%d' % (name, i // chunk), wait=1800)
    res += ab.run([{'t': 'erase', 'h': erase}, {'t': 'save'}], name + '_er')[-300:]
    errs = [l for l in res.splitlines() if 'ERR' in l or 'errors' in l]
    print('\n'.join(errs[-12:]))
    return st


def ypass_std(yA_rows, r=1200, step=6000):
    """analog rows А..Е (6) -> new А, Б, В: keep А, Б (template interior), Е -> В"""
    y0 = yA_rows[0]
    return retile.Pass('y', yA_rows, [[i] for i in range(len(yA_rows))], None, r,
                       [y0, y0 + step, y0 + 2 * step],
                       {0: [0], 1: [1], 2: [], 3: [], 4: [], 5: [2]},
                       {0: [0], 1: [], 2: [], 3: [], 4: [1]})


def xpass_std(x_axes, r=1200, step=6000, n=11):
    """analog axes 1..4 (2,3 at 1800 collapse into one interior node) -> 1..11 at 6000"""
    x0 = x_axes[0]
    return retile.Pass('x', x_axes, [[0], [1, 2], [3]], [0, 1, 3], r,
                       [x0 + step * j for j in range(n)],
                       {0: [0], 1: list(range(1, n - 1)), 2: [n - 1]},
                       {0: list(range(0, n - 2)), 1: [n - 2]})


def axis_vals(win):
    out = ab.run([{'t': 'axisinfo', 'win': list(win)}], 'axinfo')
    vals = {}
    for l in out.splitlines():
        if l.startswith('AX '):
            p = l.split(' ', 2)
            vals[p[1]] = p[2].strip().rstrip(',') if len(p) > 2 else ''
    return vals


def detect_axes(es, win):
    vals = axis_vals(win)
    ok = lambda v: v.isdigit() or (0 < len(v) <= 2 and '.' not in v)
    ax = [e for e in es if e.dxf == 'SPDSCONSTRUCTIONLINE' and len(e.sp) >= 2 and ext.inside(e, win, 1) and ok(vals.get(e.h, ''))
          and abs(e.sp[0][0] - e.sp[1][0]) + abs(e.sp[0][1] - e.sp[1][1]) > 9000]
    xs = sorted(set(round(e.sp[0][0], 3) for e in ax if abs(e.sp[0][0] - e.sp[1][0]) < 1))
    ys = sorted(set(round(e.sp[0][1], 3) for e in ax if abs(e.sp[0][1] - e.sp[1][1]) < 1))
    return xs, ys


def do_plan(sheet, r=1200, extra_excl=()):
    import sheets
    E0 = ext.load(W + r'\ext0.txt')
    f = sheets.FRAME[sheet][1]
    inn = [e for e in E0 if ext.inside(e, f, 1)]
    d = sheets.shift(sheet)
    tag = sheet.replace('.', '')
    out = ab.run([{'t': 'clonexf', 'hs': [e.h for e in inn], 'd': list(d), 'pre': 'C%s_' % tag}], 'c' + tag)
    if 'errors 0' not in out: print(out[-500:])
    sx, sy = sheets.slot(sheet)
    win = (sx - 50, sy - 50, sx + (f[2] - f[0]) + 50, sy + (f[3] - f[1]) + 50)
    es = dump(win, 'n%sa' % tag)
    xs, ys = detect_axes(es, win)
    print(sheet, 'axes x', [round(v - xs[0]) for v in xs], 'y', [round(v - ys[0]) for v in ys])
    if len(ys) == 6:
        run_pass(work_set(es, win, extra_excl), ypass_std(ys, r), 'Y%s_' % tag, 'y' + tag)
    es = dump(win, 'n%sb' % tag)
    if len(xs) == 4:
        run_pass(work_set(es, win, extra_excl), xpass_std(xs, r), 'X%s_' % tag, 'x' + tag)
    return xs, ys


def wipe(sheet, w=99000, h=60000):
    import sheets
    sx, sy = sheets.slot(sheet)
    win = (sx - 100, sy - 100, sx + w, sy + h)
    es = dump(win, 'wipe')
    hs = [e.h for e in es if ext.inside(e, win)]
    print('wipe', sheet, len(hs))
    print(ab.run([{'t': 'erase', 'h': hs}, {'t': 'save'}], 'wipe')[-200:])


def shift_box(sheet, box):
    import sheets
    dx, dy = sheets.shift(sheet)
    return (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy)


def below_axes_box(sheet):
    """analog-sheet box under the bottom axis bubbles (section details live there), in the NEW slot coords"""
    import sheets
    f = sheets.FRAME[sheet][1]
    E0 = ext.load(W + r'\ext0.txt')
    vals = axis_vals(f)
    ax = [e for e in E0 if e.h in vals and vals[e.h] in set('1234') and ext.inside(e, f, 1) and abs(e.sp[0][1] - e.sp[1][1]) > 9000]
    ylow = min(min(q[1] for q in e.sp) for e in ax)
    return shift_box(sheet, (f[0] - 10, f[1] - 10, f[2] + 10, ylow - 900))
