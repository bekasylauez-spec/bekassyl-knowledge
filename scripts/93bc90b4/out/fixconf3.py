import sys, os, pickle, collections
# step 2 per ТХ: rail 500 from axis (was 750), crane girder top +11.893 (rail head +12.000, rail Р24 107 mm)
SP = sys.argv[1]; out = sys.argv[2]
R = pickle.load(open(os.path.join(SP, 'out', 'frows.pkl'), 'rb'))
L = ['LOG|' + os.path.join(SP, 'out', 'fix3.log'), 'OUT|' + out]
def f(v): return '%.3f' % v

# ---------- sheet 8 (plan, 1:220)
X0 = 1050766.5; S = 220
def X(mm): return X0 + mm * S
def Y(mm): return mm * S
axes = {}
for r in R:
    if r[1] == 'LINE' and r[7] == 'DXK_LINE_DOT3' and X0 < r[2] < X0 + 841 * S:
        x1, y1, x2, y2 = r[9]
        if abs(y1 - y2) < 1e-6 and abs(x2 - x1) > 100 * S:
            axes[round(y1 / S, 2)] = y1
hl = collections.Counter()
exact = {}
for r in R:
    if r[1] == 'LINE' and X0 < r[2] < X0 + 841 * S and r[7] == 'Continuous':
        x1, y1, x2, y2 = r[9]
        if abs(y1 - y2) < 1e-6 and abs(x2 - x1) > 2 * S:
            k = round(y1 / S, 2); hl[k] += 1; exact[k] = y1
A, E, H, M = axes[234.02], axes[343.12], axes[397.66], axes[506.75]
rows = [  # (old runway y, axis, side, text bottom old mm, text placement 'far'|'keep')
    (exact[237.43], A, +1, 238.30),
    (exact[339.71], E, -1, 340.57),
    (exact[346.52], E, +1, 347.39),
    (exact[394.25], H, -1, 395.12),
    (exact[401.07], H, +1, 401.94),
    (exact[503.34], M, -1, 504.21),
]
TH = 2.88; GAP = 0.86   # text height and gap to the line, sheet mm
# dims first (templates still exist), then erase old dims
tick_tpl = f(X(822.22)) + ';' + f(exact[339.71] / S * S - 0.78 * S) + ';' + f(0.3 * S)
txt_tpl = f(X(823 - 1.1)) + ';' + f(E - 750 - 1.1 * S - 5.0 * S) + ';' + f(6 * S)
for pts in ([A, A + 500], [E - 500, E, E + 500], [H - 500, H, H + 500], [M - 500, M]):
    L.append('|'.join(['DIM', f(X(823)), f(1.56 * S), f(X(809.5)), f(1.1 * S), txt_tpl, tick_tpl, ';'.join(f(v) for v in pts), '1']))
for c in (E, H):
    L.append('|'.join(['ERASE', f(X(813.2)), f(c - 750 - 9 * S), f(X(826)), f(c + 750 + 9 * S), 'LINES']))
    L.append('|'.join(['ERASE', f(X(805)), f(c - 750 - 9 * S), f(X(826)), f(c + 750 + 9 * S), 'TEXT:750']))
    L.append('|'.join(['ERASE', f(X(805)), f(c - 750 - 2 * S), f(X(826)), f(c + 750 + 2 * S), 'HLINEX:' + f(X(809.5)) + ':' + f(0.05 * S)]))
for c in (E, H):
    L.append('|'.join(['ERASE', f(X(805)), f(c - 750 - 2 * S), f(X(826)), f(c + 750 + 2 * S), 'HSEG:' + ':'.join(f(X(v)) for v in (809.5, 811.5, 816.5, 818.6))]))
for ya, yb in ((226, 239), (495.5, 508)):
    L.append('|'.join(['ERASE', f(X(809.5)), f(Y(ya)), f(X(819)), f(Y(yb)), 'LINES']))
    L.append('|'.join(['ERASE', f(X(805)), f(Y(ya)), f(X(819)), f(Y(yb)), 'TEXT:750']))
    L.append('|'.join(['ERASE', f(X(809)), f(Y(ya)), f(X(819)), f(Y(yb)), 'WIPEOUT>' + f(4 * S)]))
for yo, c, side, tb in rows:
    yn = c + side * 500
    L.append('|'.join(['MOVEY', f(X(65)), f(X(812.9)), f(yo), f(yn), '0.5']))
    ynm = yn / S
    if (yo - c) * side > 0 and ((tb * S) - yo) * side > 0:
        nb = ynm + GAP                       # text on the far side already (above a runway above the axis)
    elif side > 0:
        nb = ynm + GAP                       # runway above the axis: text above the line
    else:
        nb = ynm - GAP - TH                  # runway below the axis: text below the line (no room between line and axis)
    dy = (nb - tb) * S
    dxm = 6 * S if (c == H and side < 0) else 0   # H middle-bay row: keep PB clear of the KN callouts below H
    L.append('|'.join(['MOVET', f(X(65)), f(Y(tb - 0.3)), f(X(812.9)), f(Y(tb + TH + 0.6)), f(dxm), f(dy), 'ПБ']))

# ---------- sheet 4 sections (1:150): consoles 250 toward the column, up 893
X0 = 445993; S = 150
def X(mm): return X0 + mm * S
def Y(mm): return mm * S
rep = '950=700;1006=756'
for cm in (76.02, 236.02, 316.02, 476.02):     # 3-3
    L.append('|'.join(['CONSOLE', f(X(cm - 15)), f(Y(135)), f(X(cm + 15)), f(Y(160)), f(X(cm)), '893', '450', '250', rep, '300', '23000']))
for cm in (71.37, 231.37, 311.37, 471.37):     # 2-2
    L.append('|'.join(['CONSOLE', f(X(cm - 15)), f(Y(315)), f(X(cm + 15)), f(Y(345)), f(X(cm)), '893', '450', '250', rep, '300', '50545']))
L.append('|'.join(['MOVEY', f(X(55)), f(X(480)), '50745.2', '51638.2', '0.5']))
L.append('|'.join(['MOVET', f(X(20)), f(Y(337.5)), f(X(70)), f(Y(350)), '0', '893', '*', '+11.000=+11.893']))
open(os.path.join(SP, 'out', 'fixconf3.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
