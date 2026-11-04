# Sheet shells for Block 3: copy analog sheets (frame, stamp, notes, sections, nodes), clear their plans,
# A2 -> A1 for Пм1, rename texts and sheet numbers. Runs before the plan ops.
import json
from gen import SH, AN_R3, AN_R3Y, AN_R1, AN_R1Y, AN_R1S, T, FR_A3
ops = []
def add(**k): ops.append(k); return k
def W(x0, y0, x1, y1): return [x0, y0, x1, y1]

TBL3 = ['BCEEA557', 'BCEEA558', 'BCEEA559']        # Пм3 spec: steel summary, spec body, spec header
SHEETNO3 = (38300, -27600, 39300, -26900)            # stamp sheet-number cell of an A3 frame (from its top-left)

FR = {(AN_R3[0], AN_R3Y): 'BCEE9BF2', (AN_R3[1], AN_R3Y): 'BCEE9BFA', (AN_R3[2], AN_R3Y): 'BCEE9C02', (AN_R3[3], AN_R3Y): 'BCEE9C0B',
      (AN_R3[4], AN_R3Y): 'BCEE9BEA', (AN_R1[0], AN_R1Y): 'BCEC43E9', (AN_R1[1], AN_R1Y): 'BCEC43F1', (AN_R1[2], AN_R1Y): 'BCEC43F9',
      (AN_R1[3], AN_R1Y): 'BCEC4A5B', AN_R1S: 'BCEC43E1'}
LAST = {}
def copy_sheet(src, dst, size, skip=()):
    sx, sy = src
    add(t='copywin', win=W(sx - 5, sy - size[1] - 5, sx + size[0] + 5, sy + 5), d=[dst[0] - sx, dst[1] - sy, 0], skip=list(skip) + [FR[src]], tag='sheet')
    LAST['src'] = src; LAST['d'] = [dst[0] - sx, dst[1] - sy, 0]

def frame(dst, vis, tag): add(t='clone', h=FR[LAST['src']], d=LAST['d'], tag=tag, dyn={'Видимость': vis})

def sheetno(bx, by, old, new):
    x0, y0, x1, y1 = SHEETNO3
    add(t='repl', win=W(bx + x0, by + y0, bx + x1, by + y1), pairs=[[old, new]], tag='no')

TBL1 = ['BCEC4EB3', 'BCEC4EB4', 'BCEC4EB5']        # Пм1 spec (with Ав-1): steel summary, spec body, spec header
def spec_sheet(X0, Y0, tag, big):
    src = AN_R1S if big else (AN_R3[4], AN_R3Y); tbl = TBL1 if big else TBL3
    copy_sheet(src, (X0, Y0), (42000, 29700), skip=tbl)
    frame((X0, Y0), 'А2(594х420)' if big else 'А3(420х297)', 'fr' + tag)
    if not big: add(t='erasewin', win=W(X0 + 1900, Y0 - 9300, X0 + 8400, Y0 - 7150))     # Х1 row (no opening framing here)
    add(t='erasewin', win=W(X0 + 22500, Y0 - 16600, X0 + 41800, Y0 - 14500))            # border line under the analog table
    for j, h in enumerate(tbl): add(t='clone', h=h, d=[X0 - src[0], Y0 - src[1], 0], tag='t%s_%d' % (tag, j))
    if big:
        # A1 landscape: notes and stamp texts to the new stamp corner, steel summary down to the bottom edge
        add(t='movewin', win=W(X0 + 22000, Y0 - 29705, X0 + 42005, Y0 - 20500), d=[17400, -12300, 0],
            skip=['t%s_%d' % (tag, j) for j in range(3)] + ['fr' + tag])
        add(t='edit', h='t%s_0' % tag, d=[0, -12300, 0])
        add(t='edit', h='t%s_1' % tag, d=[-1500, 0, 0]); add(t='edit', h='t%s_2' % tag, d=[-1500, 0, 0])

# ---- Пм2 (+4.500), sheets 8..12: A2 (plan 24x14.5 m) from analog Пм3 A3; sheet 12 spec A3 ----
DXA2, DYA2 = 59400 - 42000, -(42000 - 29700)
N45 = {0: ('КЖ-3.', 'КЖ-9.'), 1: ('КЖ-3,5.', 'КЖ-10,12.'), 2: ('КЖ-2,5.', 'КЖ-9,12.'), 3: ('КЖ-3,5.', 'КЖ-9,12.'), 4: ('КЖ-3,4.', 'КЖ-10,11.')}
for i in range(5):
    X0, Y0 = SH[('P45', i)]['X0'], SH[('P45', i)]['Y0']
    if i < 4:
        copy_sheet((AN_R3[i], AN_R3Y), (X0, Y0), (42000, 29700))
        frame((X0, Y0), 'А2(594х420)', 'fr45_%d' % i)
    else: spec_sheet(X0, Y0, '45', False)
    if i == 0: add(t='erasewin', win=W(X0 + 800, Y0 - 17300, X0 + 41500, Y0 - 2000))
    if i == 1: add(t='erasewin', win=W(X0 + 800, Y0 - 18600, X0 + 41500, Y0 - 2000))
    if i == 2:
        add(t='erasewin', win=W(X0 + 800, Y0 - 17800, X0 + 41500, Y0 - 2000))
        add(t='erasewin', win=W(X0 + 800, Y0 - 28500, X0 + 22500, Y0 - 17000))
    if i == 3: add(t='erasewin', win=W(X0 + 800, Y0 - 17700, X0 + 41500, Y0 - 2000))
    if i < 4:
        # A3 -> A2: lower-left content (sections, nodes) down, stamp texts and notes to the A2 stamp corner
        add(t='movewin', win=W(X0 - 5, Y0 - 29705, X0 + 25000, Y0 - 17000), d=[33500, 11500, 0], skip=['fr45_%d' % i])
        add(t='movewin', win=W(X0 + 22800, Y0 - 29705, X0 + 42005, Y0 - 20500), d=[DXA2, DYA2, 0], skip=['fr45_%d' % i])
        sheetno(X0 + DXA2, Y0 + DYA2, str(i + 1), str(i + 8))
    else: sheetno(X0, Y0, str(i + 1), str(i + 8))
    add(t='repl', win=W(X0, Y0 - 42000, X0 + 59400, Y0), tag='txt45',
        pairs=[['Пм3', 'Пм2'], ['Пм-3', 'Пм-2'], ['Блок 2', 'Блок 3'], [N45[i][0], N45[i][1]],
               ['вдоль буквенных, цифровых осей и обрамления отверстий', 'вдоль буквенных и цифровых осей']])

# ---- Пм1 (+7.000), sheets 1..6: A1 from analog Пм1 (A2); sheet 7 spec ----
DXA1, DYA1 = 84100 - 59400, -(59400 - 42000)
SRC70 = [0, 1, 2, 3, 2, 3]
TTL = {2: 'нижней зоне плиты вдоль буквенных осей', 3: 'верхней зоне плиты вдоль буквенных осей',
       4: 'нижней зоне плиты вдоль цифровых осей', 5: 'верхней зоне плиты вдоль цифровых осей'}
N70 = {0: ('КЖ-3.', 'КЖ-2.'), 1: ('КЖ-3,5.', 'КЖ-3-7.'), 2: ('КЖ-3,5.', 'КЖ-2,7.'), 3: ('КЖ-3,5.', 'КЖ-2,7.'),
       4: ('КЖ-3,5.', 'КЖ-2,7.'), 5: ('КЖ-3,5.', 'КЖ-2,7.')}
for i in range(6):
    X0, Y0 = SH[('P70', i)]['X0'], SH[('P70', i)]['Y0']
    src = SRC70[i]
    copy_sheet((AN_R1[src], AN_R1Y), (X0, Y0), (59400, 42000))
    frame((X0, Y0), 'А1(841х594)', 'fr70_%d' % i)
    add(t='movewin', win=W(X0 + 40000, Y0 - 42005, X0 + 59405, Y0 - 33300), d=[DXA1, DYA1, 0])
    if src in (0, 2):
        add(t='erasewin', win=W(X0 + 200, Y0 - 41800, X0 + 59000, Y0 - 2700))
    if src == 1:
        add(t='erasewin', win=W(X0 + 800, Y0 - 26500, X0 + 59000, Y0 - 2700))
        add(t='movewin', win=W(X0 + 20500, Y0 - 35000, X0 + 36000, Y0 - 26800), d=[66500 - 20912, -21000 + 27242, 0])
        add(t='movewin', win=W(X0 + 3500, Y0 - 35000, X0 + 19000, Y0 - 26800), d=[66500 - 3910, -10000 + 27217, 0])
    if src == 3:
        add(t='erasewin', win=W(X0 + 800, Y0 - 28500, X0 + 59000, Y0 - 2700))
        add(t='movewin', win=W(X0 + 10500, Y0 - 36500, X0 + 36000, Y0 - 28600), d=[64000 - 11384, -12000 + 29257, 0])
    sheetno(X0 + 42100, Y0 - 29700, str(src + 1), str(i + 1))
    pairs = [['Блок 2', 'Блок 3'], [N70[i][0], N70[i][1]], ['КЖ-2,5.', N70[i][1]]]
    if i in TTL:
        z = 'нижней' if i in (2, 4) else 'верхней'
        pairs.append([z + ' зоне плиты вдоль буквенных и цифровых осей', TTL[i]])
    add(t='repl', win=W(X0, Y0 - 59400, X0 + 84100, Y0), tag='txt70', pairs=pairs)

X0, Y0 = SH[('P70', 6)]['X0'], SH[('P70', 6)]['Y0']
spec_sheet(X0, Y0, '70', True)
sheetno(X0 + 17400, Y0 - 12300, '5', '7')
add(t='repl', win=W(X0, Y0 - 42000, X0 + 59400, Y0), tag='txt70s',
    pairs=[['Блок 2', 'Блок 3'], ['КЖ-3,4.', 'КЖ-3-6.']])

add(t='clone', h=T['title'], to=[-791072 + 16700, -3120000 + 9600], tag='blk3', text='Блок 3')
ERASE_B2 = dict(t='erasewin', win=W(-800000, -3060000, -480000, -2830000))     # analog Block 2 content, applied last
json.dump(ERASE_B2, open('ops_tail.json', 'w'))
json.dump(ops, open('ops_asm.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(ops))
