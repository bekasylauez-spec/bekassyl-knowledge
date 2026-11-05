# ведомость деталей 5.50: cells for the hooked lintel bars 38 (Ø25) and 39 (Ø36), cloned from the Ск5 cell (П -> Г: bottom leg away)
import sys, re; sys.path.insert(0, 'wl'); from common import *
X, Y = 3151500.0, 455939.0
CELL = ['359F1E', '359F1F', '359F21', '359F22', '359F24', '359F26', '359F27', '359F28', '359F2A', '359F2B']
ITEMS = [('38', 3400, 300, 3700), ('39', 4080, 440, 4520)]
ops = []
for j, (nm, top, hk, Ln) in enumerate(ITEMS):
    dy = -2000 * (j + 1)
    for h in CELL: ops.append(dict(t='clone', h=h, base=[0, 0], to=[0, dy], tag='G%s_%s' % (nm, h)))
    t = lambda h: 'G%s_%s' % (nm, h)
    ops += [dict(t='settext', h=t('359F26'), s=nm), dict(t='settext', h=t('359F1F'), s=str(top)), dict(t='settext', h=t('359F1E'), s=str(hk)),
            dict(t='settext', h=t('359F24'), s=str(Ln)), dict(t='erase', h=[t('359F22'), t('359F27')]),
            dict(t='pl', p=[[X + 6892, Y + 23312 + dy], [X + 5187, Y + 23312 + dy], [X + 5083, Y + 23208 + dy], [X + 5083, Y + 22684 + dy]], b=[0, 0.4142, 0, 0], tag='G%s_pl' % nm),
            dict(t='eprops', src='359F27', h=['G%s_pl' % nm])]
ops.append(dict(t='save'))
out = gx.run(ops, 'g11'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
