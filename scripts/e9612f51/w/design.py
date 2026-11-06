# БДМ Блок 3 ригели: LIRA As (ArmBars CSV) -> reinforcement per beam part, marks by identical geometry+section+design
# Rules: main Ø28 A500C (user 06.11), b>300: 4+4, 2 hoops (4 legs); b<=300: 3+3, 1 hoop (2 legs);
# доп Ø28 between main bars in the same row only where As(LIRA) > As(main); hoops A240 Ø10..Ø14, ш.100 near supports (1/4 span) / 200 middle
import json, math, sys, collections
from asbar import load

A28 = math.pi * 2.8 ** 2 / 4  # 6.158 cm2
def hoop(asw, legs, b):
    # smallest Ø with step 100 / 200 satisfying asw (cm2/m); returns (d, s_support, s_mid)
    for d in (10, 12, 14, 16):
        a = legs * math.pi * (d / 10.0) ** 2 / 4
        if a * 10 >= asw - 1e-6: return d, a
    return 16, legs * math.pi * 1.6 ** 2 / 4

def design(parts, R):
    out = []
    for p in parts:
        b, h = p['sec']; nmain = 4 if b > 300 else 3; legs = 4 if b > 300 else 2
        asm = nmain * A28
        pts = []  # (coord along beam, bot, top, asw)
        for a, bb, el, rev in p['els']:
            r = R.get(el)
            if not r: continue
            s1, s2 = r.get(1, [0, 0, 0]), r.get(2, [0, 0, 0])
            if rev: s1, s2 = s2, s1
            pts.append((a, s1[0], s1[1], s1[2])); pts.append((bb, s2[0], s2[1], s2[2]))
        if not pts: out.append(dict(p, missing=True)); continue
        mb = max(x[1] for x in pts); mt = max(x[2] for x in pts); mw = max(x[3] for x in pts)
        # доп zones: contiguous ranges where As > main
        def zones(k):
            z = []; cur = None
            for x in sorted(pts):
                need = x[k] - asm
                if need > 1e-6:
                    n = math.ceil(need / A28)
                    if cur and x[0] - cur[1] <= 600: cur[1] = x[0]; cur[2] = max(cur[2], n)
                    else: cur = [x[0], x[0], n]; z.append(cur)
            return z
        d, a1 = hoop(mw, legs, b)
        out.append(dict(p, nmain=nmain, legs=legs, maxbot=round(mb, 2), maxtop=round(mt, 2), maxasw=round(mw, 2),
                        asmain=round(asm, 2), dopbot=zones(1), doptop=zones(2), hoopd=d, asw100=round(a1 * 10, 1)))
    return out

if __name__ == '__main__':
    parts = json.load(open('parts.json'))
    R = load(sys.argv[1])
    D = design(parts, R)
    json.dump(D, open('design.json', 'w'), ensure_ascii=False)
    for x in sorted(D, key=lambda p: (p['z'], -p['sec'][1], p['dir'], p['c'], p['s'])):
        if x.get('missing'): print('MISSING', x['z'], x['dir'], x['c']); continue
        print(x['z'], x['dir'], x['c'], x['sec'], x['s'], x['e'], 'bot', x['maxbot'], 'top', x['maxtop'], 'main', x['asmain'],
              'asw', x['maxasw'], 'Ø%d' % x['hoopd'], 'dopB', [(a, b, n) for a, b, n in x['dopbot']], 'dopT', [(a, b, n) for a, b, n in x['doptop']])
