# Section 1-1 of the rigel 450×550 (4+4 Ø25, two hoops Х1 Ø10 over 3 bars each, slab 250) — edited from the analog
# 1:20 section (tags S1:<old>, staging frame at 172179,430000), analog 2-2 removed. Units = real mm (1:20 drawing).
import gx, json
S = lambda h: 'S1:' + h
xL, xR, yb, yt = 173740.0, 174190.0, 431384.0, 431934.0
ys = yt - 250                      # slab bottom
xa, xb = xL - 173, xR + 173        # slab flange breaks (analog 173)
BX = [xL + 50, xL + 167, xL + 283, xR - 50]
YBOT, YTOP = yb + 50, 431884.0
ops = []
add = lambda **k: ops.append(k)

def build(dia='25', hoop='10'):
    add(t='plset', h=S('40444A'), p=[[xR, yb], [xR, ys], [xb, ys], [xb, yt], [xa, yt], [xa, ys], [xL, ys], [xL, yb]], closed=True)
    for h, x in zip(['40444B', '404886', '40488D', '40445E'], BX):
        add(t='insat', h=S(h), at=[x, YBOT]); add(t='dyn', h=S(h), prop='Вид', value='Ø' + dia)
    for h, x in zip(['404468', '40490C', '404913', '40446F'], BX):
        add(t='insat', h=S(h), at=[x, YTOP]); add(t='dyn', h=S(h), prop='Вид', value='Ø' + dia)
    for h, x in zip(['404492', '40600F'], BX[:2]):
        add(t='insat', h=S(h), at=[x, YBOT + 11])
        add(t='dyn', h=S(h), prop='Расстояние1', value=BX[2] - BX[0])
        add(t='dyn', h=S(h), prop='Расстояние2', value=YTOP - YBOT)
    yd = 431078
    for h, (p, q) in zip(['404452', '40498B', '4049B4', '40499A', '404465'], [(xL, BX[0]), (BX[0], BX[1]), (BX[1], BX[2]), (BX[2], BX[3]), (BX[3], xR)]):
        add(t='dimpts', h=S(h), p1=[q, yb, 0], p2=[p, yb, 0], dl=[p, yd, 0])
    add(t='dimpts', h=S('4044EF'), p1=[xL, yb, 0], p2=[xR, yb, 0], dl=[xR, 430736, 0])
    xv = 173476
    for h, (p, q) in zip(['404455', '404458', '40445B'], [(yb, YBOT), (YBOT, 431904), (431904, yt)]):
        add(t='dimpts', h=S(h), p1=[BX[0], p, 0], p2=[BX[0], q, 0], dl=[xv, q, 0])
    add(t='dimpts', h=S('4044EE'), p1=[xa, yt, 0], p2=[xL, yb, 0], dl=[173287, yb, 0])
    for h, x in (('2CB014', xb), ('2CB015', xa)):
        add(t='mcset', h=h, set={'StartPoint': [x, ys], 'EndPoint': [x, yt], 'ClipZonePoint': [x, yt], 'Length': yt - ys})
    add(t='move', h=['2CB018'], d=[xa - 173592, 0])
    add(t='erase', h=['2CB19C'])
    add(t='clone', h='S6:4308C2', base=[267729.5, 432053.2], to=[173146.4 + xa - 173592, 432053.8], tag='SEC1_ML')
    add(t='levelval', h='SEC1_ML', old='+4.395', value='+3.950', tag='SEC1_ML')
    add(t='combsegs', h='2CB019', segs=[[[x, YTOP - 1], [x + 88, 432097]] for x in BX], start=[BX[3] + 88, 432097], end=[BX[0] + 88, 432097])
    add(t='mcset', h='2CB019', set={'SecondLine': '(ф%s)' % dia})
    yk = YBOT - 151
    add(t='combsegs', h='2CB01A', segs=[[[x, YBOT - 2], [x + 70, yk]] for x in BX], start=[BX[3] + 110, yk], end=[BX[0] + 70, yk])
    add(t='mcset', h='2CB01A', set={'SecondLine': '(ф%s)' % dia})
    ym = (YBOT + YTOP) / 2
    add(t='combsegs', h='2CB07F', segs=[[[BX[2] + 15, ym], [xR + 175, ym]], [[BX[3] + 15, ym], [xR + 175, ym]]])
    add(t='spmove', h='2CB07F', items=[[0, xR + 175, ym]])
    add(t='mcset', h='2CB07F', set={'SecondLine': '(ф%s)' % hoop})

if __name__ == '__main__':
    build()
    # analog section 2-2 (x > 174500 in the staging frame) not needed for Рм-1..3
    import os
    keep = []
    out = gx.run([{'t': 'list', 'win': [174500, 430500, 176500, 433000]}], 'l22')
    er = [l.split('\t')[2] for l in open(os.environ['TEMP'] + r'\gq_log.txt', encoding='utf-8-sig') if l.startswith('L\t') and l.split('\t')[1] != 'SPDSFORMAT']
    ops.append(dict(t='erase', h=er))
    ops.append(dict(t='save'))
    out = gx.run(ops, 'sec1')
    print(len(er), [l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'no ' in l][:20])
