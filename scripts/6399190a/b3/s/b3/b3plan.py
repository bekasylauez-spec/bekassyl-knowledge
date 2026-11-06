# Block 3 column plan: scheme coords (AR, axis 1 = 0) + LIRA key
import json
AXX = {'14': 87700, '15': 94300, '16': 100300, '17': 106300, '18': 112300, '19': 118300, '20': 124300, '21': 130300, '22': 136300}
AXY = {'А': 0, 'В': 10500, 'Г': 15500, 'Е': 21000, 'И': 28000, 'Л': 34000, 'М': 39500}
XN = list(AXX)
def lx(ax): return {'14': 86.1, '22': 135.1}.get(ax, round(AXX[ax] / 1000 - 1.2, 2))
LY = {'А': -1.35, 'В': 9.15, 'Г': 14.15, 'Е': 19.65, 'И': 26.65, 'Л': 32.65, 'М': 38.15}
C = []
def add(id_, x, y, bx, by, lira, kind='main', top_of=None):
    C.append(dict(id=id_, x=x, y=y, bx=bx, by=by, lira=lira, kind=kind, top_of=top_of))
# 900x1100 rows А, В, М (scheme centres; edge columns flush with outer faces)
for row, yc in (('А', 300), ('В', 10850), ('М', 39200)):
    for ax in XN:
        x = {'14': 87500, '22': 136100}.get(ax, AXX[ax])
        add('%s/%s' % (row, ax), x, yc, 900, 1100, [lx(ax) if ax != '22' else 135.1, LY[row]])
# 700x700 rows Г, Е, И, Л
rowsx = {'Г': XN, 'Е': XN, 'И': XN, 'Л': ['14', '20', '21', '22']}
for row, axs in rowsx.items():
    for ax in axs:
        x = {'14': 87400, '22': 136200}.get(ax, AXX[ax])
        add('%s/%s' % (row, ax), x, AXY[row], 700, 700, [lx(ax) if ax != '22' else 135.1, LY[row]])
# 500x500 between axes 21-22 (LIRA 132.1), rows А, В
add('А/21-22', 133300, 0, 500, 500, [132.1, -1.35])
add('В/21-22', 133300, 10650, 500, 500, [132.1, 9.15])
# stair columns 500x500 from ±0.000 (LIRA only)
for (lxk, lyk, x, y, i) in ((132.1, 1.8, 133300, 3150, 'А-В/21-22a'), (135.1, 1.8, 136300, 3150, 'А-В/22a'),
                             (132.1, 4.45, 133300, 5800, 'А-В/21-22b'), (135.1, 4.45, 136300, 5800, 'А-В/22b')):
    add(i, x, y, 500, 500, [lxk, lyk], 'stair')
# upper 500x500 from +7.000: on beams (В-Г, Е-И) and over Г/Е columns at axes 18,19
for ax in ('18', '19'):
    add('В-Г/%s' % ax, AXX[ax], 13000, 500, 500, [lx(ax), 11.65], 'upper')
    add('Е-И/%s' % ax, AXX[ax], 23500, 500, 500, [lx(ax), 22.15], 'upper')
    add('Г/%s+' % ax, AXX[ax], 15500, 500, 500, [lx(ax), 14.15], 'upper', top_of='Г/%s' % ax)
    add('Е/%s+' % ax, AXX[ax], 21000, 500, 500, [lx(ax), 19.65], 'upper', top_of='Е/%s' % ax)
if __name__ == '__main__':
    import collections
    print(len(C), collections.Counter(c['kind'] for c in C))
    json.dump(C, open('plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
