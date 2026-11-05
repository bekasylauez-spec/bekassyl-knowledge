"""Лист 3.1 «Опалубочный чертеж фундамента Фм-1» (A3, 1:100): clone of plan 2.1 without column marks + section marks."""
import sys, os, json
import ab, pl_ob

W21 = [-1552803, -1749172, -1510803, -1719472]
WOLD = [-1107303, -1749172, -1018203, -1707172]
X0 = -1107303.0; Y0F = -1749172.0
D = X0 - W21[0]
A3 = ['37E5F2', '37E5F3', '37E5F4', '37E5F6']; A3X0, A3Y0 = -1743303.0, -1749172.0
SEC = '357D3A'

# column marks on 2.1 (SPDS notes «Км-…») and the notes MTEXT
ab.run([{'t': 'geomdump', 'win': W21, 'file': os.path.abspath('w/g21now.txt')}], 'g')
km = set()
for l in open('w/g21now.txt', encoding='utf-8'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'T' and f[2] == 'SPDSNOTEPOSITION' and f[7].startswith('Км'): km.add(f[1])
si = pl_ob.sheetinfo(W21)
skip = {e['h'] for e in si['E'] if e['t'] == 'SPDSFORMAT' or (e['t'] == 'INSERT' and e['ext'][1] < W21[1] + 1000) or (e['t'] == 'MTEXT' and e['lay'] == 'О_Формат')}
notes = [e['h'] for e in si['E'] if e['t'] == 'MTEXT' and e['lay'] == 'Размеры' and e['ext'][1] < W21[1] + 7000]
title = [e['h'] for e in si['E'] if e['t'] == 'MTEXT' and e['lay'] == 'Размеры' and e['ext'][3] > W21[3] - 1500]
hs = [e['h'] for e in si['E'] if e['h'] not in skip and e['h'] not in km and e['h'] not in notes]
V = sorted([e for e in si['E'] if e['t'] == 'SPDSCONSTRUCTIONLINE' and abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: e['pts'][0][0])
H = sorted([e for e in si['E'] if e['t'] == 'SPDSCONSTRUCTIONLINE' and abs(e['pts'][0][1] - e['pts'][1][1]) < 1], key=lambda e: e['pts'][0][1])
X = [e['pts'][0][0] + D for e in V]; Y = [e['pts'][0][1] for e in H]
print('clone', len(hs), 'skip Км', len(km), 'title', title, 'notes', notes)

O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
     {'t': 'eraseregion', 'win': WOLD, 'keep': [SEC]},
     {'t': 'clonexf', 'hs': A3, 'd': [X0 - A3X0, Y0F - A3Y0], 'pre': 'a3_31_'},
     {'t': 'clonexf', 'hs': hs, 'd': [D, 0], 'pre': 'c31_'}]
for h in title:
    O.append({'t': 'settext', 'h': 'c31_' + h, 's': '{\\LОпалубочный чертеж фундамента Фм-1 на отм. -0.500}'})
O += [{'t': 'settext', 'h': 'a3_31_37E5F4', 's': 'Опалубочный чертеж фундамента Фм-1'}, {'t': 'settext', 'h': 'a3_31_37E5F6', 's': '3.1'}]
# section marks (short, across the element, as in the analog 3.1)
xb, yb = X[2], Y[1]
for k, (word, pts) in enumerate((('1', [[X[6] + 600, yb - 1500 - 800], [X[6] + 600, yb + 1500 + 800]]),
                                 ('2', [[X[6] - 1000 - 800, yb + 600], [X[6] + 1000 + 800, yb + 600]]),
                                 ('3', [[(X[2] + X[3]) / 2, Y[0] + 175 + 800], [(X[2] + X[3]) / 2, Y[0] - 175 - 800]]))):
    tg = 'sec31_%d' % k
    O.append({'t': 'clone', 'h': SEC, 'tag': tg})
    O.append({'t': 'secset', 'h': tg, 'pts': pts, 'word': word})
O.append({'t': 'erase', 'h': [SEC]})
O.append({'t': 'mtext', 'at': [X0 + 2300, Y0F + 5200], 'h': 250, 'w': 19500, 'layer': 'Размеры',
          's': '1. Фундамент Фм-1 монолитный: подушки 2000х3000х1000 (низ -1.500), балки 350х600 (низ -1.100), верх -0.500. Бетон С20/25 (B25) W6 F150.\\P'
               '2. Бетонная подготовка С8/10 t=100. Разрезы 1-1...3-3 и армирование - см. лист 3.2.'})
O.append({'t': 'vpset2', 'layout': '3.1', 'media': 'ISO_full_bleed_A3_(420.00_x_297.00_MM)', 'win': [X0, Y0F, X0 + 42000, Y0F + 29700], 'scale': 100})
O.append({'t': 'save'})
if len(sys.argv) > 1:
    out = ab.run(O, 'g31', 1500)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'secset' in l or 'eraseregion' in l)[-1200:])
