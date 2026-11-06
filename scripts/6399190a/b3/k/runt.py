import sys, json, lib, ab, place, gt
TY = json.load(open('types_t.json', encoding='utf-8'))
NOTE7 = 'В местах примыкания ригелей промежуточных уровней хомуты шаг 100 по всей высоте колонны (сетки С1 только в узле верха).'
sel = sys.argv[1:]
for k, T in enumerate(TY):
    if sel and T['mark'] not in sel: continue
    if T['mark'] in ('Км-1', 'Км-3', 'Км-4', 'Км-5'): T['note7'] = NOTE7
    X0, Y0 = 300000 + k * 29700, 350000
    lib.OPS.clear()
    lib.op(t='eraseregion', win=[X0 - 2, Y0 - 2, X0 + 29702, Y0 + 21002], mode='intersect')
    st = len(lib.OPS); info = gt.build(X0, Y0, T, '4.%d' % (k + 2)); place.resolve(lib.OPS, st)
    lay = '4.%d' % (k + 2)
    lib.op(t='laydel', name=lay)
    lib.op(t='laycopy', src='0', dst=lay)
    lib.op(t='vpset2', layout=lay, media='ISO_full_bleed_A2_(594.00_x_420.00_MM)', win=[X0, Y0, X0 + 29700, Y0 + 21000], scale=50)
    lib.op(t='save')
    out = ab.run(lib.OPS, 'gt_%d' % k, 1500)
    errs = [l for l in ab.log().splitlines() if 'ERR' in l or 'no handle' in l or 'not found' in l]
    print(T['mark'], info, len(lib.OPS), 'errs', len(errs)); print('\n'.join(errs[:25]))
