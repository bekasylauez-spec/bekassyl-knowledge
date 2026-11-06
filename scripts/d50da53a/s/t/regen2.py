import sys, json, time, mb, gcol
TY = json.load(open(mb.S + r'\coltypes.json', encoding='utf-8'))
res = {}
try: res = json.load(open(mb.S + r'\w\colinfo.json', encoding='utf-8'))
except Exception: pass
for k, T in enumerate(TY):
    if T['mark'] not in sys.argv[1:]: continue
    x0 = gcol.SL0 + k * gcol.SW; y0 = gcol.O0[1]
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, y0 - 3000, x0 + gcol.SW + 1, y0 + 24000]}]
    o, info = gcol.build(T, k, '4.%d' % (k + 2)); ops += o
    lay = '4.%d' % (k + 2)
    ops += [{'t': 'laydel', 'name': lay}, {'t': 'laycopy', 'src': 'x4.1', 'dst': lay}, {'t': 'vpset2', 'layout': lay, 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [x0, y0, x0 + 29700, y0 + 21000], 'scale': 50}, {'t': 'save'}]
    i = 0; CH = 120
    while i < len(ops):
        t0 = time.time(); out = mb.run(ops[i:i + CH], 'rg_%d_%d' % (k, i), 1200)
        errs = [l for l in out.splitlines() if 'ERR' in l or 'timeout' in l]
        print(T['mark'], i, len(ops), '%.0fs' % (time.time() - t0), errs[:6], flush=True)
        if any('timeout' in e for e in errs): sys.exit(1)
        i += CH
    res[T['mark']] = info
    json.dump(res, open(mb.S + r'\w\colinfo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
