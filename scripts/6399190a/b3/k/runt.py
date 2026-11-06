import sys, json, lib, ab, place, gt
TY = json.load(open('types_t.json', encoding='utf-8'))
NOTE7 = 'В уровнях промежуточных ригелей - хомуты ш.100 по всей высоте, сетки С1 только в верхнем узле.'
sel = sys.argv[1:]
for k, T in enumerate(TY):
    if sel and T['mark'] not in sel: continue
    if T['mark'] in ('Км-1', 'Км-3', 'Км-4', 'Км-5'): T['note7'] = NOTE7
    X0, Y0 = 300000 + k * 29700, 350000
    lib.OPS.clear()
    lib.op(t='eraseregion', win=[X0 - 2, Y0 - 2, X0 + 29702, Y0 + 21002], mode='intersect')
    st = len(lib.OPS); info = gt.build(X0, Y0, T, '4.%d' % (k + 2)); place.resolve(lib.OPS, st)
    lay = '4.%d' % (k + 2)
    lib.op(t='save')
    errs = []
    for i in range(0, len(lib.OPS), 25):
        out = ab.run(lib.OPS[i:i + 25], 'gt_%d_%d' % (k, i), 300)
        if 'timeout' in out[:300]: errs.append('TIMEOUT %d' % i); break
        errs += [l for l in ab.log().splitlines() if 'ERR' in l or 'no handle' in l or 'not found' in l]
    print(T['mark'], info, len(lib.OPS), 'errs', len(errs)); print('\n'.join(errs[:25]))
