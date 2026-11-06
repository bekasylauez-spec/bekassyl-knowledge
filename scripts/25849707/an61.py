# analog «Ресторан 6.1 Ригель» sheet Рм-1: entity inventory helpers
SRC = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad\an\a61.dwg'
AN0 = (-232572.0, 411799.0)          # analog frame min; frame 31500 x 14850
ROWS = []
for l in open(r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad\an\list61.txt', encoding='utf-8-sig'):
    r = l.rstrip('\n').split('\t')
    if len(r) < 5 or 'NaN' in r[4]: continue
    ROWS.append((r[1], r[2], r[3], [float(v) for v in r[4][1:].split(',')]))
def handles(x0, y0, x1, y1):
    return [h for t, h, L, e in ROWS if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5]
SHEET = handles(-232572, 411799, -201072, 426649) + ['407C02', '40647F']
SECS = handles(-212200, 427400, -208800, 429300)
