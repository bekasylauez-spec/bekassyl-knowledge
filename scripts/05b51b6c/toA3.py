"""Replace an A3x3 sheet frame by an A3 frame (clone of sheet 1.2 frame+stamp), move the drawing inside, retarget the layout."""
import sys, json, os
import ab, pl_ob

A3 = ['37E5F2', '37E5F3', '37E5F4', '37E5F6']           # SPDSFORMAT, stamp insert, sheet-name MTEXT, sheet-number MTEXT (sheet 1.2)
A3X0, A3Y0 = -1743303.0, -1749172.0
HOLD_Y = 60000                                           # tables parked above the row


def convert(name, win, title_text, sheet_no, keep_out=()):
    x0, y0, x1, y1 = win
    si = pl_ob.sheetinfo(win)
    E = si['E']
    old_frame = [e['h'] for e in E if e['t'] == 'SPDSFORMAT']
    old_stamp = [e['h'] for e in E if e['t'] == 'INSERT' and e['ext'][1] < y0 + 1000] + si['stamp']
    tables = si['table']
    notes = [e['h'] for e in E if e['t'] == 'MTEXT' and e['lay'] == 'Размеры' and e['ext'][3] - e['ext'][1] >= 200 and e['ext'][0] > x0 + 60000]
    skip = set(old_frame + old_stamp + tables + notes + list(keep_out))
    C = [e for e in E if e['h'] not in skip]
    bx0 = min(e['ext'][0] for e in C); by0 = min(e['ext'][1] for e in C)
    bx1 = max(e['ext'][2] for e in C); by1 = max(e['ext'][3] for e in C)
    W, H = bx1 - bx0, by1 - by0
    # inner A3 area: x0+2000 .. x0+41500, y0+500 .. y0+29200; keep the bottom-right stamp (185x55) free
    tx = x0 + 2000 + (39500 - W) / 2
    ty = y0 + 29200 - 300 - H
    print(name, 'content %.0f x %.0f' % (W, H), 'fits' if W <= 39500 and H <= 28700 else 'DOES NOT FIT', 'bottom gap %.0f' % (ty - y0))
    O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
         {'t': 'clonexf', 'hs': A3, 'd': [x0 - A3X0, y0 - A3Y0], 'pre': 'a3_%s_' % name},
         {'t': 'movewin', 'win': [bx0 - 1, by0 - 1, bx1 + 1, by1 + 1], 'd': [tx - bx0, ty - by0], 'skip': list(skip)},
         {'t': 'erase', 'h': old_frame + old_stamp}]
    if tables: O.append({'t': 'move', 'h': tables, 'd': [0, HOLD_Y]})
    for i, h in enumerate(notes):   # notes -> left bottom corner
        O.append({'t': 'moveto', 'h': h, 'idx': 0, 'to': [x0 + 2300, y0 + 5200 - 1200 * i]})
    O.append({'t': 'settext', 'h': 'a3_%s_37E5F4' % name, 's': title_text})
    O.append({'t': 'settext', 'h': 'a3_%s_37E5F6' % name, 's': sheet_no})
    O.append({'t': 'vpset2', 'layout': name, 'media': 'ISO_full_bleed_A3_(420.00_x_297.00_MM)', 'win': [x0, y0, x0 + 42000, y0 + 29700], 'scale': 100})
    return O


if __name__ == '__main__':
    J = {'2.1': ([-1552803, -1749172, -1463703, -1707172], 'Схема расположения элементов на отм. -0.500'),
         '2.2': ([-1463703, -1749172, -1374603, -1707172], 'Схема расположения элементов на отм. 0.000'),
         '2.3': ([-1374603, -1749172, -1285503, -1707172], 'Схема расположения элементов на отм. +6.200'),
         '2.4': ([-1285503, -1749172, -1196403, -1707172], 'Схема расположения элементов на отм. +11.400')}
    O = []
    for n in sys.argv[2:]:
        w, t = J[n]
        O += convert(n, w, t, n)
    O.append({'t': 'save'})
    if sys.argv[1] == 'run':
        out = ab.run(O, 'toA3', 1200)
        print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'movewin' in l or 'vpset2' in l or 'clonexf' in l)[-2500:])
