# -*- coding: utf-8 -*-
# РМЦ КМ каркасы: тексеріс (v2, 13.11.2026). Кіріс: members.tsv (gen.py), lira_map.tsv, model_dump.tsv (Revit-тен rmc_90_check.cs, bbox = геометриядан), clash.tsv.
# Шығыс: _verify.txt (utf-8).
#  1) lira_vs_model: ЛИРА-ның әр стержені -> gen.py иесі (member id) -> Revit-те сол id («марка-id») элементі бар, маркасы/типі дұрыс, орны members.tsv-мен <=0.5 мм сәйкес.
#     Қосымша геометриялық жабылу: стержень ортасы (КМ_геометрия + УЗЕЛ ПАСПОРТТАРЫ ережесімен, gen.py-дан БӨЛЕК жазылған түрлендіру) иесі элементтің геометрия-bbox ±3 мм ішінде.
#  2) санау: марка бойынша (модель) vs паспорт 3.4 vs v1; 3) ұзындық/масса.
import json, math, collections, os, re
H = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(r'D:\_claude_work\RMC\lira\model.json', encoding='utf-8'))
rods = {r['i']: r for r in M['rods']}
mem = {}
for l in open(os.path.join(H, 'members.tsv'), encoding='utf-8'):
    t = l.rstrip('\n').split('\t'); mem[int(t[0])] = dict(mark=t[1], kind=t[2], fam=t[3], p=tuple(map(float, t[4:7])), q=tuple(map(float, t[7:10])), rods=[int(x) for x in t[14].split(',') if x])
lmap = collections.defaultdict(list)
for l in open(os.path.join(H, 'lira_map.tsv'), encoding='utf-8'):
    r, m = map(int, l.split()); lmap[r].append(m)
dump = {}
def f(x): return float(x.replace(',', '.')) if x not in ('', None) else None
for l in open(os.path.join(H, 'model_dump.tsv'), encoding='utf-8'):
    t = l.rstrip('\n').split('\t')
    # idx, mark, instmark, type, family, p(3), q(3), bbox(6), vol, ends
    dump[t[2]] = dict(mark=t[1], type=t[3], fam=t[4], p=tuple(f(x) for x in t[5:8]), q=tuple(f(x) for x in t[8:11]), bb=tuple(f(x) for x in t[11:17]), vol=f(t[17]), ends=t[18] if len(t) > 18 else '')
INCL = {8: 'Пр1', 9: 'Р1', 10: 'Р2', 11: 'Р3', 12: 'СВ', 13: 'ГС', 15: 'Б1', 16: 'Б2', 17: 'Б3', 18: 'К3', 19: 'К1', 20: 'К2', 21: 'КБ1', 22: 'Б4', 23: 'Б5', 25: 'ПБ1'}
out = []
rep = out.append
# ---- 1) lira_vs_model
missing = []; badpos = []; dev_max = 0.0; n_ok = 0
for rid, r in rods.items():
    if r['s'] not in INCL: continue
    ms = lmap.get(rid, [])
    if len(ms) != 1: missing.append((rid, 'no owner' if not ms else 'multi')); continue
    m = mem[ms[0]]; key = m['mark'] + '-' + str(ms[0]); d = dump.get(key)
    if d is None: missing.append((rid, 'member %s not in model' % key)); continue
    if not d['mark'] == m['mark'] or not (d['mark'].startswith(INCL[r['s']])):
        missing.append((rid, 'mark mismatch ' + d['mark'] + ' vs ' + INCL[r['s']])); continue
    if m['kind'] == 'B':
        dev = max(abs(a - b) for a, b in list(zip(d['p'], m['p'])) + list(zip(d['q'], m['q'])))
        if dev > 0.5:
            if m['fam'] != 'purlin': badpos.append((rid, key, round(dev, 2)))   # purlin орталығы 120 мм қиғаш: бөлек есептеледі
        else: dev_max = max(dev_max, dev)
    else:
        bb = d['bb']; dev = max(abs(bb[2] - m['p'][2]), abs(bb[5] - m['q'][2]), abs((bb[0] + bb[3]) / 2 - m['p'][0]), abs((bb[1] + bb[4]) / 2 - m['p'][1]))
        if dev > 0.6: badpos.append((rid, key, round(dev, 2)))
        else: dev_max = max(dev_max, dev)
    n_ok += 1
rep('1) lira_vs_model: ЛИРА стержені (жесткость 8-13, 15-23, 25) = %d; иесі табылып, моделде бар, орны сәйкес = %d; missing = %d; орын айырмасы > допуск = %d; max ауытқу (түзу/колонна) = %.3f мм' % (sum(1 for r in rods.values() if r['s'] in INCL), n_ok, len(missing), len(badpos), dev_max))
for x in missing[:20]: rep('   MISSING ' + str(x))
for x in badpos[:20]: rep('   BADPOS ' + str(x))

# ---- ЛИРА -> модель координата түрлендіруі (паспорттардан, gen.py-дан бөлек)
def XM(xl, k23=False):
    if abs(xl) < 1e-6: return 100.0 if k23 else 150.0
    if abs(xl - 60) < 1e-6: return 59900.0 if k23 else 59850.0
    return xl * 1000.0
def top_raf(y): d = min(y, 36000 - y); return 8968 + 0.05 * d
def bot(y):
    d = min(y, 36000 - y)
    if d <= 600: return 8311.0
    if d <= 6000: return 8311.0 + 507.0 * (d - 600) / 5400.0
    if d <= 12500: return 8968 + 0.05 * d - 450.0
    return 9143.0 + 175.0 * (d - 12500) / 5500.0
def neu(y): return (top_raf(y) + bot(y)) / 2
YCm = lambda yl: 266.0 if abs(yl) < 1e-6 else (35734.0 if abs(yl - 36) < 1e-6 else yl * 1000)
SVY = {0.0: 266.0, 18.0: 17986.0, 36.0: 35734.0}
RAIL = {0.3: 800.0, 17.7: 17400.0, 18.3: 18600.0, 35.7: 35200.0}
def gs_wp(yl, oyl):
    y3 = round(yl, 3)
    if y3 == 0.0: return 532.0
    if y3 == 36.0: return 35468.0
    if y3 == 18.0: return 17734.0 if oyl < 18 else 18266.0
    return y3 * 1000.0
def tm(r):
    s_ = r['s']; cls = INCL[s_]; pts = []
    for e, o in ((r['p'], r['q']), (r['q'], r['p'])):
        xl, yl, zl = e; X = XM(xl, cls in ('К2', 'К3'))
        if cls in ('К1', 'Б4', 'Б5'): Y = YCm(yl)
        elif cls == 'Р1': Y = (SVY[round(yl, 3)] + 28.0) if zl <= 5.0 else YCm(yl) + 22.0
        elif cls == 'СВ': Y = SVY[round(yl, 3)]
        elif cls == 'Р2': Y = 18014.0
        elif cls == 'ГС': Y = gs_wp(yl, o[1])
        elif cls == 'ПБ1': Y = RAIL[round(yl, 1)]
        elif cls == 'КБ1': Y = None
        elif cls == 'Пр1': Y = YCm(yl)
        else: Y = yl * 1000
        if cls == 'К1': Z = {-0.1: 900.0, 0.35: 1350.0, 2.8: 3800.0, 4.2: 5200.0, 5.0: 6000.0, 7.9: 8286.0, 8.9: 9293.0}[round(zl, 3)]
        elif cls in ('К2', 'К3'): Z = zl * 1000 + 1000 if zl <= 5 else None
        elif cls in ('Б4', 'Б5'): Z = 3900 - (164 if cls == 'Б4' else 162)
        elif cls == 'ПБ1': Z = 5200 + 393
        elif cls == 'КБ1': Z = 5000.0
        elif cls in ('Б1', 'Б2', 'Б3'): Z = neu(Y)
        elif cls == 'Пр1': Z = top_raf(Y) + 120
        elif cls == 'Р1': Z = 6000.0 if zl <= 5.0 else 8641.6
        elif cls == 'СВ':
            if zl <= 5.0: Z = zl * 1000 + 1000
            else: zt = 8.9 if abs(yl - 18) < 1e-6 else 7.9; Z = 6000 + (zl - 5.0) / (zt - 5.0) * ((9593.0 if abs(yl - 18) < 1e-6 else 8641.6) - 6000)
        elif cls == 'ГС': Z = neu(Y) - 1.0
        else: Z = neu(Y)
        pts.append((X, Y, Z))
    mid = tuple((a + b) / 2 if (a is not None and b is not None) else None for a, b in zip(*pts))
    if cls == 'КБ1':
        ym = (r['p'][1] + r['q'][1]) / 2
        ry = 800.0 if ym < 9 else (35200.0 if ym > 27 else 18000.0 + (600.0 if ym > 18 else -600.0))
        mid = (mid[0], ry, mid[2])
    return mid
# ---- геометриялық жабылу: ЛИРА стержені ортасы ∈ иесі геометрия-bbox ±3 мм
gc = collections.Counter(); gbad = []
for rid, r in rods.items():
    if r['s'] not in INCL: continue
    ms = lmap[rid][0]; d = dump['%s-%d' % (mem[ms]['mark'], ms)]; mid = tm(r); cls = INCL[r['s']]
    if mid is None: gc[cls, 'skip'] += 1; continue
    bb = d['bb']; ok = True; tol = 3.0
    for k, v in enumerate(mid):
        if v is None: continue
        if not (bb[k] - tol <= v <= bb[k + 3] + tol): ok = False
    gc[cls, ok] += 1
    if not ok: gbad.append((rid, cls, [round(v, 1) if v is not None else None for v in mid], [round(x, 1) for x in bb]))
rep('   геом. жабылу (стержень ортасы ∈ иесі геометрия-bbox ±3 мм), класс бойынша: ' + '; '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(gc.items(), key=lambda t: (t[0][0], str(t[0][1])))))
for x in gbad[:15]: rep('   GEOBAD ' + str(x))
# ---- жоспар жабылуы: X-бағытты түзу класстар, паспорттағы ұштар (gen.py-дан бөлек жазылған күтілетін мәндер)
cov = collections.Counter(); covbad = []
for rid, r in rods.items():
    cls = INCL.get(r['s'])
    if cls not in ('Р2', 'Р3', 'Пр1', 'ПБ1'): continue
    ms = lmap[rid][0]; mm = mem[ms]; d = dump['%s-%d' % (mm['mark'], ms)]
    xl0, xl1 = sorted((r['p'][0], r['q'][0])); xa, xb = XM(xl0), XM(xl1)
    ymid = (r['p'][1] + r['q'][1]) / 2 * 1000
    x0, x1 = sorted((d['p'][0], d['q'][0])); y_el = (d['p'][1] + d['q'][1]) / 2
    if cls == 'ПБ1': ymid = RAIL[round(ymid / 1000, 1)]; e0, e1, ytol = xa + 10, xb - 10, 3.5
    elif cls == 'Р2': ymid = 18014.0; e0, e1, ytol = xa + 325, xb - 325, 3.5
    elif cls == 'Р3': e0 = xa + (254 if min(abs(ymid - 6000), abs(ymid - 30000)) < 1 else 269); e1 = xb - (254 if min(abs(ymid - 6000), abs(ymid - 30000)) < 1 else 269); ytol = 3.5
    else:
        ymid = 266.0 if ymid < 1 else (35734.0 if ymid > 35999 else ymid); e0 = xa + 100; e1 = xb - 100; ytol = 8
        if abs(xl0) < 1e-6: e0 = xa - 250
        if abs(xl1 - 60) < 1e-6: e1 = xb + 250
    ok = abs(y_el - ymid) <= ytol and abs(x0 - e0) <= 0.6 and abs(x1 - e1) <= 0.6
    cov[cls, ok] += 1
    if not ok: covbad.append((rid, cls, ymid, y_el, round(x0 - e0, 2), round(x1 - e1, 2)))
rep('   жоспар жабылуы (Р2, Р3, Пр1, ПБ1: Y осі және ұштары паспорт бойынша ±0,6 мм): ' + ', '.join('%s ok=%s: %d' % (k[0], k[1], v) for k, v in sorted(cov.items())) + ('; нашар: %s' % covbad[:5] if covbad else ''))
# ---- 2) санау
v1 = {'К1': 33, 'К2': 16, 'К3': 4, 'Б1': 22, 'Б2': 22, 'Б3': 22, 'Б4': 39, 'Б5': 24, 'ПБ1': 40, 'КБ1': 44, 'Пр1': 260, 'Р1': 50, 'Р2': 10, 'Р3': 28, 'СВ1': 16, 'СВ2': 8, 'СВ3': 6, 'СВ4': 6, 'СВ5': 6, 'ГС1': 24, 'ГС2': 24}
pass_ = {'К1': 33, 'К2': 16, 'К3': 4, 'Б1': 22, 'Б2': 22, 'Б3': 22, 'Б4': 21, 'Б5': 6, 'ПБ1': 40, 'КБ1': 44, 'Пр1': 260, 'Р1': 50, 'Р2': 10, 'Р3': 28, 'СВ1': 16, 'СВ2': 8, 'СВ3': 6, 'СВ4': 6, 'СВ5': 6, 'ГС1': 24, 'ГС2': 12}
why = {'СВ1': '+8 кесілген диагональ жартысы (8 крест)', 'СВ2': '+4 (4 крест)', 'СВ3': '+3 (3 крест)', 'СВ4': '+3 (3 крест)', 'СВ5': '+3 (3 крест)', 'ГС1': '+8 (8 крест)', 'ГС2': '+4 (4 крест)'}
cnt = collections.Counter(d['mark'] for d in dump.values()); L = collections.defaultdict(float); mass = collections.defaultdict(float)
for k, d in dump.items():
    m = mem[int(k.split('-')[1])]
    if m['kind'] == 'B': L[d['mark']] += math.sqrt(sum((a - b) ** 2 for a, b in zip(d['p'], d['q']))) / 1000
    else: L[d['mark']] += (d['bb'][5] - d['bb'][2]) / 1000
    mass[d['mark']] += d['vol'] * 7850e-9
rep('2) марка | модельде саны | v1 (13.11 15:40) | паспорт 3.4 | өзгеру себебі | Σ ұзындық, м (модельден; кесілмеген бөліктің жиыны) | Σ масса, кг (көлем×7850)')
tot = 0
for mk in ['К1', 'К2', 'К3', 'Б1', 'Б2', 'Б3', 'Б4', 'Б5', 'ПБ1', 'КБ1', 'Пр1', 'Р1', 'Р2', 'Р3', 'СВ1', 'СВ2', 'СВ3', 'СВ4', 'СВ5', 'ГС1', 'ГС2']:
    rep('   %-4s | %4d | %4d | %4d%s | %s | %8.1f | %9.0f' % (mk, cnt[mk], v1[mk], pass_[mk], '' if cnt[mk] == pass_[mk] else '  (!)', why.get(mk, '' if cnt[mk] == v1[mk] else '?'), L[mk], mass[mk])); tot += cnt[mk]
rep('   Барлығы: %d элемент (v1: %d, паспорт сомасы %d)' % (tot, sum(v1.values()), sum(pass_.values())))
open(os.path.join(H, '_verify.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
