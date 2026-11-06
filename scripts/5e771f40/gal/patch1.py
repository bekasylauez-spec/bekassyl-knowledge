import io
s = io.open('b4rig.py', encoding='utf-8').read()
old = """            bot = ['2CAF83', '2CB036', '2CB03D', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CB04B', '2CAFFC']
            if nb == 3: bot = ['2CAF83', '2CB036', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CAFFC']; s.add(t='erase', h=[Q('2CB03D'), Q('2CB04B'), Q('2CB080')])
            for hh, x in zip(bot, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yB)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            for hh, x in zip(top, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yT)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            hoops = ['2CB003'] if nb == 3 else ['2CB003', '2CB080']
            for hh, x in zip(hoops, BX):
                ix, iy = g(x, yB + 10.8)
                s.add(t='insat', h=Q(hh), at=[ix, iy])
                # dynamic parameters of a cloned block do not regenerate -> explode to the hoop polyline and stretch it
                s.add(t='explode', h=Q(hh), pre=Q(hh) + 'P')
                hp = Q(hh) + 'P0'
                # hoop around the bars: right / top outer edge = bar centre + 14 (Ø28/2) + 10 (hoop)
                s.add(t='pfit', h=hp, right=g(x + (BX[2] - BX[0]) + 24, 0)[0], top=g(0, yT + 24)[1])"""
new = """            bot = ['2CAF83', '2CB036', '2CB03D', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CB04B', '2CAFFC']
            if nb == 3: bot = ['2CAF83', '2CB036', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CAFFC']; s.add(t='erase', h=[Q('2CB03D'), Q('2CB04B'), Q('2CB080')])
            if nb == 6:
                for k in range(2):
                    for lst, src in ((bot, '2CB036'), (top, '2CB044')):
                        t_ = '%s_X%d' % (src, k); s.add(t='clone', h=Q(src), tag=Q(t_)); lst.insert(2, t_)
            for hh, x in zip(bot, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yB)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            for hh, x in zip(top, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yT)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            cover = 3 if nb == 6 else 2                      # one hoop spans BX[i]..BX[i+cover]
            hoops = [('2CB003', BX[0])] if nb == 3 else [('2CB003', BX[0]), ('2CB080', BX[-1 - cover])]
            for hh, x in hoops:
                ix, iy = g(x, yB + 10.8)
                s.add(t='insat', h=Q(hh), at=[ix, iy])
                # dynamic parameters of a cloned block do not regenerate -> explode to the hoop polyline and stretch it
                s.add(t='explode', h=Q(hh), pre=Q(hh) + 'P')
                hp = Q(hh) + 'P0'
                # hoop around the bars: right / top outer edge = bar centre + 14 (Ø28/2) + 10 (hoop)
                s.add(t='pfit', h=hp, right=g(x + (BX[cover] - BX[0]) + 24, 0)[0], top=g(0, yT + 24)[1])
            # side bars Ø12 (h > 700): both faces inside the hoop legs, equal spacing between the rows
            ns = M.get('nside', 0)
            ysides = [yB + (yT - yB) * (i + 1) / (ns + 1) for i in range(ns)]
            for i, yy in enumerate(ysides):
                for side, xx in (('L', BX[0] + 7), ('R', BX[-1] - 7)):
                    t_ = '%sS%s%d' % (pre, side, i)
                    s.add(t='clone', h=Q('2CAF83'), tag=t_); s.add(t='insat', h=t_, at=g(xx, yy)); s.add(t='dyn', h=t_, prop='Вид', value='Ø12')"""
assert old in s; s = s.replace(old, new)
old2 = """            ym = (yB + yT) / 2
            legs = [[g(BX[-1] + 15, ym), g(b + 190, ym)]] + ([[g(BX[2] + 15, ym), g(b + 190, ym)]] if nb == 4 else [])"""
new2 = """            ym = (yB + yT) / 2 if not ns else (yB + ysides[0]) / 2
            legs = [[g(BX[-1] + 15, ym), g(b + 190, ym)]] + ([[g(BX[cover] + 15, ym), g(b + 190, ym)]] if nb >= 4 else [])"""
assert old2 in s; s = s.replace(old2, new2)
old3 = """            s.add(t='moveto', h=Q('2CB016'), idx=0, to=g(b / 2.0, h + 470))"""
new3 = """            if ns:      # side-bar callout: comb from the right-face bars to a shelf right of the section
                t_ = '%sSC' % pre
                ysh = ysides[-1] + 120
                s.add(t='clone', h=Q('2CB01A'), tag=t_)
                segs = [[g(BX[-1] - 7, yy), g(b + 120, ysh)] for yy in ysides]
                s.add(t='combsegs', h=t_, segs=segs, start=g(b + 120, ysh), end=g(b + 120 + 220, ysh), trim=True)
                s.add(t='mcset', h=t_, set={'FirstLine': M['side_pos'], 'SecondLine': '(ф12)'})
            s.add(t='moveto', h=Q('2CB016'), idx=0, to=g(b / 2.0, h + 470))"""
assert old3 in s; s = s.replace(old3, new3)
old4 = """        for i, (pos, dia, L, n) in enumerate(rows):
            r = 6 + i; R = r + 1
            cells_t += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
            nums += [[r, 3, dia, I], [r, 9, L, I]]
            forms += [[r, 10, '%d' % n, I], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]"""
new4 = """        for i, (pos, dia, L, n) in enumerate(rows):
            r = 6 + i; R = r + 1
            cells_t += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
            nums += [[r, 3, dia, I]]
            if L is None:
                cells_t += [[r, 9, 'пог.м.']]
                forms += [[r, 10, '%.2f' % n, F], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*1' % (R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]
            else:
                nums += [[r, 9, L, I]]
                forms += [[r, 10, '%d' % n, I], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]"""
assert old4 in s; s = s.replace(old4, new4)
old6 = """        last = 5 + nd; conc = last + 2"""
new6 = """        last = 5 + nd; conc = last + 2
        side_row = next((6 + i for i, q in enumerate(rows) if q[2] is None), 0)"""
assert old6 in s; s = s.replace(old6, new6)
old5 = """                     [6, 6, 'TEXT:---'], [6, 7, 'Table({T:%s}).Evaluate(Sum(M6:M%d))' % (m[sp], last + 1), F], [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]])]"""
new5 = """                     [6, 6, 'TEXT:---'], [6, 5, 'TEXT:---'],
                     [6, 3, 'Table({T:%s}).M%d' % (m[sp], side_row + 1), F] if side_row else [6, 3, 'TEXT:---'],
                     [6, 7, 'Table({T:%s}).Evaluate(%s)' % (m[sp], '+'.join('M%d' % (r_ + 1) for r_ in range(5, last + 1) if r_ != side_row)), F],
                     [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]])]"""
assert old5 in s; s = s.replace(old5, new5)
io.open('b4rig.py', 'w', encoding='utf-8').write(s)
print('ok')
