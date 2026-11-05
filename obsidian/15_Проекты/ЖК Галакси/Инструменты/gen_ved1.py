import json, sys, gx
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
R = json.load(open('w/k41_list4.json'))
ops = []
def add(**k): ops.append(k)
S = {'10B811': '320', '10B810': '550', '10B814': '320', '10B819': '1190',
     '10B842': '200', '10B841': '400', '10B845': '200', '10B84A': '800',
     '10B80A': '428', '10B802': '428', '10B804': '428', '10B801': '428', '10B822': '1910',
     '10B889': '303', '10B881': '303', '10B883': '303', '10B880': '303', '10B88F': '1410'}
for h, s in S.items(): add(t='settext', h=h, s=s)
# rows Ск3, Ск4, Х3, Х4, Шп1, Шп2 out; Х1, Х2 up by two rows
er = [r['h'] for r in R if 31900 < r['x0'] and r['x1'] < 38300 and ((31500 <= r['y0'] < 35500) or (19500 <= r['y0'] < 27500))]
mv = [r['h'] for r in R if 31900 < r['x0'] and r['x1'] < 38300 and 27500 <= r['y0'] < 31500]
add(t='erase', h=er + ['10B7A7'])
add(t='movegrp', h=mv, d=[0, 4000])
# накладки table out (keep the steel ACAD_TABLE)
er2 = [r['h'] for r in R if 31900 < r['x0'] and r['x1'] < 38400 and 12800 < r['y0'] and r['y1'] < 18600 and r['t'] != 'ACAD_TABLE']
add(t='erase', h=er2)
# grid: 4 rows + header, one Поз|Эскиз pair (same lines as the analog block)
for y in (31500, 33500, 35500, 37500):
    add(t='pl', p=[W(31965, y + 2000), W(38265, y + 2000), W(38265, y), W(31965, y)], closed=True, layer='TEXT 2.5')
    add(t='pl', p=[W(33465, y + 2000), W(33465, y)], layer='TEXT 2.5')
add(t='pl', p=[W(31965, 39500), W(31965, 40700), W(38265, 40700), W(38265, 39500)], layer='0')
add(t='pl', p=[W(33465, 40700), W(33465, 39500)], layer='0')
add(t='mtext', at=W(32715, 40100), h=270, att=5, s='Поз.', style='Isocpeur', layer='TEXT 2.5')
add(t='mtext', at=W(35865, 40100), h=270, att=5, s='Эскиз', style='Isocpeur', layer='TEXT 2.5')
add(t='mtext', at=W(35115, 41100), h=300, att=5, s='Ведомость деталей', style='Isocpeur', layer='TEXT 2.5')
add(t='save')
json.dump(ops, open('ops/k41ved.json', 'w'), ensure_ascii=False)
print(len(ops), len(er), len(mv), len(er2))
if '--run' in sys.argv: print(gx.run(ops, 'k41ved')[-600:])
