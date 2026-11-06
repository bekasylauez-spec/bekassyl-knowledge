# Sheet 6.1 «Ригель Рм-1» = imported analog sheet «Ресторан 6.1 Рм-1» (tags A1:<old>) edited to our beam.
# Elevation only (sections/tables in later steps). Beam: row y −1000, axes 1-4, −125..20175, 450×550, top −0.100 / +3.950.
import gx, json, sys
from rg import zones
A = lambda h: 'A1:' + h
T1 = 175307.0                       # axis 1 on the sheet (beam end −125 = analog end 175182)
def X(x): return T1 + x
YT, YB = 468700.0, 468150.0         # beam top / bottom
YTB, YBB = 468670.0, 468200.0       # top / bottom bar
AX = [0, 6800, 13250, 20050]
COLS = [(-125, 375), (6550, 7050), (13000, 13500), (19675, 20175)]
END0, END1 = -125, 20175
ops = []
add = lambda **k: ops.append(k)

# ---- columns, breaks, axes
for h, (a, b) in zip(['40159B', '4018B7', '4018BD', '4018C3'], COLS):
    add(t='plset', h=A(h), p=[[X(a), 468797], [X(b), 468797], [X(b), 467970], [X(a), 467970]], closed=True)
add(t='erase', h=[A('4018BA'), A('4018C0')])
for (ht, hb), (a, b) in zip([('2CA6EC', '2CA6ED'), ('2CA72C', '2CA72D'), ('2CA732', '2CA733'), ('2CA738', '2CA739')], COLS):
    for h, y in ((ht, 468797.4), (hb, 467970.4)):
        mid = (a + b) / 2
        add(t='sp_set', h=h, pts=[[0, X(a), y], [1, X(mid), y], [2, X(b), y], [3, X(b), y], [4, X(mid), y], [5, X(a), y], [6, X(mid), y]])
add(t='erase', h=['2CA72F', '2CA730', '2CA735', '2CA736'])
for h, x, v in zip(['2CA688', '2CA68A', '2CA6AA', '2CA6CA'], AX, '1234'):
    add(t='axis', h=h, s=[X(x), 468700], e=[X(x), 466361], val=v)
add(t='erase', h=['2CA69A', '2CA6BA'])

# ---- beam outline between column faces, bars, Ск1
faces = [(COLS[i][1], COLS[i + 1][0]) for i in range(3)]
for h, (a, b) in zip(['40159C', '402404', '403897'], faces):
    add(t='plset', h=A(h), p=[[X(b), YB], [X(b), YT], [X(a), YT], [X(a), YB]], closed=True)
add(t='erase', h=[A('403898'), A('403899')])
add(t='plset', h=A('4015A8'), p=[[X(END0 + 20), YTB], [X(END1 - 20), YTB]], layer='диам25')
add(t='plset', h=A('4015AE'), p=[[X(END0 + 20), YBB], [X(END1 - 20), YBB]], layer='диам25')
L = 250                                                     # Ск1 legs = 10d (Ø25)
e0, e1 = X(END0) + 20, X(END1) - 20
add(t='plset', h=A('4015C1'), p=[[e0 + L, YBB + 20], [e0 + 25, YBB + 20], [e0, YBB + 45], [e0, YTB - 45], [e0 + 25, YTB - 20], [e0 + L, YTB - 20]])
add(t='plset', h=A('4069BF'), p=[[e1 - L, YBB + 20], [e1 - 25, YBB + 20], [e1, YBB + 45], [e1, YTB - 45], [e1 - 25, YTB - 20], [e1 - L, YTB - 20]])
add(t='erase', h=[A('4274A8'), A('4274AA'), '2CABD0', '2CABD2'])  # analog pos 2 (Ø12) not needed

# ---- hoop zones: lines + chain dims
HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
      '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
      '403870', '40386A', '40386D']
ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
hl, zd, ed = list(HL), list(ZD), list(ED)
NH = 0; ZINFO = []
for i, (a, b) in enumerate(faces):
    segs, lines, cnt = zones(a, b); NH += cnt; ZINFO.append((segs, lines, cnt))
    for x in lines:
        add(t='plset', h=A(hl.pop(0)), p=[[X(x), YBB], [X(x), YTB]], layer='диам10')
    for s0, s1, txt in segs:
        h = A(zd.pop(0))
        add(t='dimpts', h=h, p1=[X(s0), YB, 0], p2=[X(s1), YB, 0], dl=[X(s1), 467342, 0])
        add(t='dimtext', h=h, s=txt if 'х' in txt else '')
    for k, (p, q) in enumerate(((AX[i], lines[0]), (lines[-1], AX[i + 1]))):
        hh = A(ed.pop(0)); add(t='dimpts', h=hh, p1=[X(q), YB, 0], p2=[X(p), YB, 0], dl=[X(p), 467342, 0])
        # short end dims: text on a shelf like the analog (left one right of the hoop, right one under the last hoop)
        add(t='dimtx', h=hh, at=[X(lines[0]) + 34, 467096, 0] if k == 0 else [X(p) - 19, 466980, 0])
add(t='erase', h=[A(h) for h in hl + zd + ed])

# ---- axis chain + total, height chain
for h, (p, q) in zip(['401296', '40129A', '40129E'], zip(AX, AX[1:])):
    add(t='dimpts', h=A(h), p1=[X(p), 466361, 0], p2=[X(q), 466361, 0], dl=[X(q), 466773, 0])
add(t='erase', h=[A('4012A2'), A('4012A5')])
add(t='dimpts', h=A('401292'), p1=[X(AX[0]), 466361, 0], p2=[X(AX[-1]), 466361, 0], dl=[X(AX[-1]), 466411, 0])
add(t='dimpts', h=A('4015A4'), p1=[X(END0), YT, 0], p2=[X(END0), YB, 0], dl=[174210, YB, 0])
add(t='dimpts', h=A('4015AD'), p1=[X(END0), YB, 0], p2=[X(END0) + 20, YBB, 0], dl=[174745, YBB, 0])
add(t='dimpts', h=A('401933'), p1=[X(END0) + 20, YBB, 0], p2=[X(END0) + 20, YTB, 0], dl=[174745, YTB, 0])

# ---- splices Н3 (Ø25, L250): top in span 2-3 middle, bottom right of axes 2 and 3 (+500/+1000), as analog
mid23 = (AX[1] + AX[2]) / 2.0
TOPC = [mid23 - 250, mid23 + 250]
BOT = [[AX[1] + 500, AX[1] + 1000], [AX[2] + 500, AX[2] + 1000]]
def plate(h, c, y): add(t='plset', h=A(h), p=[[X(c) - 125, y - 15], [X(c) - 125, y + 15], [X(c) + 125, y + 15], [X(c) + 125, y - 15]], closed=True)
plate('4038F3', TOPC[0], YTB); plate('4038F2', TOPC[1], YTB)
plate('403948', BOT[0][0], YBB); plate('403947', BOT[0][1], YBB)
plate('4039A0', BOT[1][0], YBB); plate('40399F', BOT[1][1], YBB)
add(t='dimpts', h=A('4038F1'), p1=[X(TOPC[0]), YTB, 0], p2=[X(AX[1]), YT, 0], dl=[X(AX[1]), 469559, 0])
add(t='dimpts', h=A('4038F5'), p1=[X(TOPC[1]), YTB, 0], p2=[X(TOPC[0]), YTB, 0], dl=[X(TOPC[0]), 469559, 0])
for (h1, h2), (c1, c2), ax in zip([('403992', '40394A'), ('4039A5', '4039A2')], BOT, AX[1:3]):
    add(t='dimpts', h=A(h1), p1=[X(c1), YB, 0], p2=[X(ax), YB, 0], dl=[X(ax), 467665, 0])
    add(t='dimpts', h=A(h2), p1=[X(c2), YBB, 0], p2=[X(c1), YBB, 0], dl=[X(c1), 467665, 0])
add(t='move', h=['2CA8E9'], d=[X(TOPC[0]) - 185182, 0])
add(t='move', h=['2CA8FB'], d=[X(BOT[0][0]) - 183682, -150])
add(t='move', h=['2CA91A'], d=[X(BOT[1][0]) - 192482, -150])
for h in ('2CA8E9', '2CA8FB', '2CA91A'): add(t='mcset', h=h, set={'FirstLine': 'Н3'})

# ---- callouts
for h, (segs, lines, cnt) in zip(['2CA725', '2CAA7C', '2CAA7D'], ZINFO):
    x = X(lines[1] + 300)
    add(t='spmove', h=h, items=[[0, x, 469238.6], [1, x, YBB], [2, x, YTB]])
    add(t='mcset', h=h, set={'SecondLine': '(ф25)'})
add(t='erase', h=['2CAA7E'])
yk = (YBB + 20 + YTB - 20) / 2
add(t='spmove', h='2CA72A', items=[[1, e0, yk]])
add(t='move', h=['2CAA80'], d=[e1 - 196562, 0]); add(t='spmove', h='2CAA80', items=[[1, e1, yk]])
add(t='move', h=['2CABCE'], d=[X(END1) - 196582, -150]); add(t='mcset', h='2CABCE', set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф10)'})
# sections 1-1, one per span in the 200 zone
for h, (segs, lines, cnt) in zip(['2CA727', '2CABCB', '2CABCD'], ZINFO):
    x = X(lines[2] - 700)
    add(t='secset', h=h, pts=[[x, 469793.5], [x, 465833.7]], word='1')
add(t='erase', h=['2CA728', '2CABCC', '2CABD3', '2CABD4'])

# ---- level marks: −0.100 (analog value) + one-line multilayer +3.950 cloned from analog 6.6
add(t='erase', h=['2CABD5'])
add(t='clone', h='B6:42FC64', base=[267758, 468285], to=[173261, 468700], tag='R61_ML')
add(t='levelval', h='R61_ML', old='+4.395', value='+3.950', tag='R61_ML')
add(t='save')

if __name__ == '__main__':
    json.dump(dict(NH=NH, ZINFO=ZINFO, TOPC=TOPC, BOT=BOT), open(gx.S + r'\w\r61.json', 'w'), ensure_ascii=False)
    out = gx.run(ops, 'r61')
    print(len(ops), [l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'no ' in l][:30])
    print('hoop positions', NH)
