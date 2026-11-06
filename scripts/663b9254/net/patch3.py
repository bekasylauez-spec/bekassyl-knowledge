s = open('gen3.py', encoding='utf-8').read()
def R(a, b_, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a))
    s = s.replace(a, b_)
# 1. inserted spec rows get the template texts too
R("""            cells.extend([[r, 0, lab], [r, 3, '%d' % d_], [r, 9, '%d' % Lr], [r, 10, '%d' % q]])""",
  """            cells.extend([[r, 0, lab], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, '%d' % d_], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, '%d' % Lr], [r, 10, '%d' % q]])""")
# 2. steel table moves down by the inserted rows
R("""add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
add(t='evalf')""",
  """add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
NEXTRA = max(nh_extra, 0) + max(nsk_extra, 0) + max(npos_extra, 0) + max(nm_extra, 0)
if NEXTRA: add(t='movegrp', h=[STM], d=[0, -400.0 * NEXTRA])
add(t='evalf')""")
# 3. hoop label in section 1-1 clear of the axis bubble
R("""add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * h / 2 + 120]""",
  """add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * h * 0.72 + 150]""")
# 4. upper storey: section 1-1 in the middle of its hoop zone, notes 2/3 above the splice dims
R("""s1y = [SPLV[0] + 2450] + ([SPLV[1] + 2050] if len(SPLV) > 1 else [])""",
  """s1y = [SPLV[0] + 2450] + ([(SPLV[1] + 1250 + L[-1] - BEAMS[-1]) / 2] if len(SPLV) > 1 else [])""")
R("""    y2 = SPLV[1] + 2200; add(t='note', l1='2', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XC], angle=math.pi, **NOTEo)
    y3 = SPLV[1] + 3000; add(t='note', l1='3', l2=DIA, origin=W(CX - 355, y3), targets=[W(x, y3) for x in XO], angle=math.pi, **NOTEo)""",
  """    room = (L[-1] - BEAMS[-1]) - (SPLV[1] + 1200)
    if room >= 1100:
        y2 = SPLV[1] + 1200 + room * 0.3; add(t='note', l1='2', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XC], angle=math.pi, **NOTEo)
        y3 = SPLV[1] + 1200 + room * 0.75; add(t='note', l1='3', l2=DIA, origin=W(CX - 355, y3), targets=[W(x, y3) for x in XO], angle=math.pi, **NOTEo)
    else:
        y2 = SPLV[1] + 1200 + max(room, 300) / 2; add(t='note', l1='2, 3', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XF], angle=math.pi, **NOTEo)""")
# 5. mesh labels follow the taller mesh drawings
R("""add(t='note', l1='10', l2='ш.100', origin=W(18186, 10698), targets=[W(18186, y) for y in ry], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190E'), items=[[1, SX + xr, SY + 11686]]); add(t='mcset', h=T('11190E'), set={'FirstLine': '10'})""",
  """add(t='note', l1='10', l2='ш.100', origin=W(18186, 10698 - (LMh - LMb)), targets=[W(18186, y) for y in ry], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190E'), items=[[1, SX + xr, SY + 11686 - (LMh - LMb)]]); add(t='mcset', h=T('11190E'), set={'FirstLine': '10'})""")
R("""add(t='note', l1='10', l2='ш.100', origin=W(12980, 11792), targets=[W(x, 11792) for x in rx], arrow='oblique', **NOTE)""",
  """ya = y0 + 389 + (LMh - LMb) * 0.5
add(t='note', l1='10', l2='ш.100', origin=W(12980, ya), targets=[W(x, ya) for x in rx], arrow='oblique', **NOTE)""")
open('gen3.py', 'w', encoding='utf-8').write(s)
print('ok')
