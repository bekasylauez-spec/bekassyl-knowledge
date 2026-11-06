import io
b = io.open('b4rig.py', encoding='utf-8').read()
# 1) 7-char levels (+10.500): kit mark holds 6 chars -> clone a Galaxy mark with a 7-char value (E3B69 «+10.250»)
helper = '''

def level_ops(s, h, base, value, off1, off2):
    """set the value of the SPDS level mark h placed at base (point 0)"""
    if len(value) <= 6:
        s.add(t='levelval', h=h, old='-0.100', value=value, tag=h)
        return
    t = h + '_L7'
    s.add(t='clone', h='E3B69', tag=t)
    s.add(t='mcset', h=t, set={'Scale': 50})
    s.add(t='levelval', h=t, old='+10.250', value=value, tag=t)
    s.add(t='moveto', h=t, idx=0, to=base)
    s.add(t='spmove', h=t, items=[[2, base[0] + off2, base[1]], [1, base[0] + off1, base[1] + 300]])
    s.add(t='erase', h=[h])


class Sheet:'''
assert '\n\nclass Sheet:' in b
b = b.replace('\n\nclass Sheet:', helper, 1)
old1 = """        s.add(t='moveto', h=T('A5:4015A3'), idx=0, to=[x0 + 400, s.YT])
        s.add(t='levelval', h=T('A5:4015A3'), old='-0.100', value=M['level'], tag=T('A5:4015A3'))"""
new1 = """        s.add(t='moveto', h=T('A5:4015A3'), idx=0, to=[x0 + 400, s.YT])
        level_ops(s, T('A5:4015A3'), [x0 + 400, s.YT], M['level'], -2346.9, -1726.4)"""
assert old1 in b; b = b.replace(old1, new1)
old2 = """            s.add(t='levelval', h=Q('2CB018'), old='-0.100', value=M['level'], tag=Q('2CB018'))"""
new2 = """            level_ops(s, Q('2CB018'), g(-173, h), M['level'], -1734.1, -1113.7)"""
assert old2 in b; b = b.replace(old2, new2)
# 2) bottom доп callout: to the right, just above the bottom row (as the analog section 3-3), not below the dimensions
old3 = """                else:
                    ysh = yB - 330
                    segs = [[g(xx, yy - 2), g(xx - (yy - ysh) * 0.45, ysh)] for xx, yy in pts]
                    xe = [q[1][0] for q in segs]
                    s.add(t='combsegs', h=t, segs=segs, start=[max(xe), segs[0][1][1]], end=[min(xe) - SSC * 220, segs[0][1][1]], trim=True)"""
new3 = """                else:
                    ysh = yB + 105 + (60 if any(yy > yB + 50 for _, yy in pts) else 0)
                    segs = [[g(xx, yy + 2), g(b + 120, ysh)] for xx, yy in pts]
                    s.add(t='combsegs', h=t, segs=segs, start=g(b + 120, ysh), end=g(b + 120 + 220, ysh), trim=True)"""
assert old3 in b; b = b.replace(old3, new3)
# hoop callout must stay clear of the bottom доп shelf
old4 = """            ym = (yB + yT) / 2 if not ns else (yB + ysides[0]) / 2"""
new4 = """            ym = (yB + yT) / 2 if not ns else max((yB + ysides[0]) / 2, yB + 260)"""
assert old4 in b; b = b.replace(old4, new4)
io.open('b4rig.py', 'w', encoding='utf-8').write(b)
print('ok')
