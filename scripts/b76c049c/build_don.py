# -*- coding: utf-8 -*-
"""2-кезең: аналог терезелерін s4_an_donors.json-ға қосу (handle, type, bb абсолют, txt, ins)"""
import pickle, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = pickle.load(open(sys.argv[1], 'rb'))
J = json.load(open(r'D:\_claude_work\otst\s4\s4_an_donors.json', encoding='utf-8'))
X = lambda i: -41822 + 59400 * i
Y0 = -1593693
J.setdefault('bb', {}); J.setdefault('txt', {})


def win(name, i, rel, extra=(), inserts=True, skip=()):
    w = [X(i) + rel[0], Y0 + rel[1], X(i) + rel[2], Y0 + rel[3]]
    hs, ty = [], {}
    for e in D:
        if e['h'] in skip: continue
        b = e['bb']; ok = False
        if b and b[0] >= w[0] - 1 and b[1] >= w[1] - 1 and b[2] <= w[2] + 1 and b[3] <= w[3] + 1: ok = True
        if inserts and e['t'] == 'INSERT' and e['txt'] == 'vcBlockST1-1-1':
            x, y = e['ex']['ins']
            if w[0] - 1 <= x <= w[2] and w[1] <= y <= w[3]: ok = True
        if e['h'] in extra: ok = True
        if not ok: continue
        hs.append(e['h']); ty[e['h']] = e['t']
        J['bb'][e['h']] = [round(v, 1) for v in b] if b else None
        if e['t'] in ('TEXT', 'MTEXT', 'INSERT', 'DIMENSION'):
            J['txt'][e['h']] = e['txt']
            if 'ins' in e['ex']: J['ins'][e['h']] = list(e['ex']['ins']) + ([0, e['ex'].get('h', 0)] if e['t'] != 'INSERT' else [])
    J['wins'][name] = dict(win=w, h=hs, types=ty)
    print(name, len(hs))


win('spec_fm', 5, [40300, 20600, 59000, 41300])
win('ved_fm', 5, [30800, 26600, 40100, 40900])
win('ved_fm2', 5, [48823, 16009, 57823, 17706], inserts=False)       # Шп1 жолы (an08 төменгі кесте)
win('steel_fm', 5, [23200, 1700, 36800, 7300])
win('kr1', 5, [2800, 1300, 17000, 8000])
win('spec_sm', 9, [40300, 27000, 59000, 41300])
win('ved_sm', 9, [29400, 22400, 38800, 40000])
win('steel_sm', 9, [41400, 18200, 56500, 23700])
win('obr', 9, [0, 0, 0, 0], extra=('2D4651',), inserts=False)
win('spec_el', 0, [40300, 5900, 59000, 11600])
win('vyp_txt', 8, [3000, 20000, 33500, 32000], inserts=False)
# vyp_txt: тек «Выпуски из днища» мәтіндері қалсын
J['wins']['vyp_txt']['h'] = [h for h in J['wins']['vyp_txt']['h'] if 'Выпуски' in (J['txt'].get(h) or '') or 'шаг' in (J['txt'].get(h) or '')]
print('vyp', [(h, J['txt'][h]) for h in J['wins']['vyp_txt']['h']])
json.dump(J, open(r'D:\_claude_work\otst\s4\s4_an_donors.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
