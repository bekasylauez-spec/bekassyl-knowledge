# arbitrary node levels: floors = every beam level [[z, h]] (h = 0: level without a beam, e.g. slab on grade), splice = [z] (bars break)
s = open('gen3.py', encoding='utf-8').read()
def R(a, b_, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a))
    s = s.replace(a, b_)
R("""SPLV = [Y(z) for z, h in FL[:-1]]                       # splice above every floor except the roof""",
  """SPLV = [Y(z) for z in TY.get('splice', [z for z, h in FL[:-1]])]   # splice above the main floors only""")
# beams only where h > 0
R("""for lv, bh in zip(L[1:], BEAMS):
    for x0, x1""", """for lv, bh in zip(L[1:], BEAMS):
    if bh <= 0: continue
    for x0, x1""")
# level marks: L0 -> base 18C36, top -> 18C39, intermediates -> 18C37, 18C3A, then clones of 18C37; values set with levelset after regen
s0 = s.index("# level marks: template marks at y 9700")
s1 = s.index("# section marks 1-1")
NEWLV = """# level marks: L0 -> base 18C36, top -> 18C39, intermediates -> 18C37, 18C3A, clones of 18C37; values by levelset after a regen
def lvs(v): return ('+' if v > 0 else '-') + ('%.3f' % abs(v)).replace('.', ',')
ZS = [TY['L0']] + [z for z, hh_ in FL]
mk = [(R_('18C36'), 9700.0)] + [None] * (len(L) - 2) + [(R_('18C39'), 19300.0)]
spare = [(R_('18C37'), 11700.0), (R_('18C3A'), 15500.0)]
for i in range(1, len(L) - 1):
    if spare: mk[i] = spare.pop(0)
    else:
        tg = PRE + 'LVC%d' % i
        add(t='clone', h=R_('18C37'), base=[0, 0], to=[0, 0], tag=tg); mk[i] = (tg, 11700.0)
for hh_, y0 in spare: add(t='erase', h=[hh_])
LVOPS = []
for i, ((h_, y0), y) in enumerate(zip(mk, L)):
    if h_.startswith(PRE) and h_[len(PRE):] in ('18C36', '18C37', '18C3A', '18C39'): KR(h_[len(PRE):])
    add(t='movegrp', h=[h_], d=[0, y - y0])
    LVOPS.append(dict(t='levelset', h=h_, value=lvs(ZS[i]), tag=h_))
"""
s = s[:s0] + NEWLV + s[s1:]
# sections / notes: middle of the longest hoop zone above each splice
R("""s1y = [SPLV[0] + 2450] + ([(SPLV[1] + 1250 + L[-1] - BEAMS[-1]) / 2] if len(SPLV) > 1 else [])""",
  """def zone_mid(lo_y, hi_y=1e9):
    best = None
    for i in range(len(L) - 1):
        a_ = max(L[i], lo_y); b2 = min(L[i + 1] - BEAMS[i], hi_y)
        if b2 - a_ > (best[1] - best[0] if best else 0): best = (a_, b2)
    return best
ZN = []
for k_, sp in enumerate(SPLV):
    nxt = SPLV[k_ + 1] if k_ + 1 < len(SPLV) else 1e9
    ZN.append(zone_mid(sp + 1200, nxt))
s1y = [(a_ + b2) / 2 for a_, b2 in ZN]""")
R("""    POS = [('1', XC, 0), ('2', XO, 1)]
    ynote = [SPLV[0] + 3000, SPLV[0] + 3800]""",
  """    POS = [('1', XC, 0), ('2', XO, 1)]
    ynote = [s1y[0] - 700, s1y[0] + 700]""")
R("""    y1 = SPLV[0] + 2400; add(t='note', l1='1'""", """    y1 = s1y[0] - 700; add(t='note', l1='1'""")
# chain: drop zero-length pieces (levels without beams)
R("""for (y1, y2, st, k) in segs:
    o = dict(""", """for (y1, y2, st, k) in segs:
    if y2 - y1 < 1: continue
    o = dict(""")
# meshes: every beam node with its own count
R("""NMESH_TOT = NMESH * NODES""", """NMESH_TOT = sum(int(round((bh - 100) / 100)) + 1 for bh in BEAMS if bh > 0)""")
open('gen3.py', 'w', encoding='utf-8').write(s)
print('ok')
