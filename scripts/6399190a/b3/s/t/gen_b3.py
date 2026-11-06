# Block 3 column sheets 4.2..: per type, erase slot, rebuild with gcol (hoop step mode from Asw), layout A2 1:50
import sys, json, time, os
import mb, gcol
from regen3 import with_retry
TY = json.load(open(mb.S + r'\b3\types_b3.json', encoding='utf-8'))
if __name__ == '__main__':
    res = {}
    try: res = json.load(open(mb.S + r'\w\colinfo_b3.json', encoding='utf-8'))
    except Exception: pass
    for k, T in enumerate(TY):
        if sys.argv[1:] and T['mark'] not in sys.argv[1:]: continue
        gcol.STEP[0] = None if T['hoop'] == 'std' else float(T['hoop'])
        x0 = gcol.SL0 + k * gcol.SW; y0 = gcol.O0[1]
        lay = '4.%d' % (k + 2)
        ops = [{'t': 'eraseregion', 'win': [x0 - 1, y0 - 3000, x0 + gcol.SW + 1, y0 + 24000]}, {'t': 'laydel', 'name': lay}]
        o, info = gcol.build(T, k, lay); ops += o
        OB = r'D:\РАБОЧКА\От Маке\Завод\Обезвоживание\КЖ Помещение обезвоживания.dwg'
        def lvs(v): return '+%d,%03d' % (v // 1000, v % 1000)
        top = T['base'] + T['levels'][-1]; bot = top - T['beams'][-1]
        for pre, hh, v in (('M%d:' % k, '4E95AC', top), ('N%d:' % k, '4E95AA', bot)):
            if v >= 10000:
                yv = gcol.O0[1] + 6950 + (v - T['base'])
                ops += [{'t': 'import', 'file': OB, 'h': ['4EF372'], 'base': [-598253.005, -1731772.311], 'to': [x0 + 4150, yv], 'pre': pre},
                        {'t': 'levelval', 'h': pre + '4EF372', 'old': '+13,700', 'value': lvs(v)},
                        {'t': 'erase', 'h': ['C%d:%s' % (k, hh)]}]
        ops += [{'t': 'laycopy', 'src': '4.2' if k > 0 else '4.1', 'dst': lay},
                {'t': 'vpset2', 'layout': lay, 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [x0, y0, x0 + 29700, y0 + 21000], 'scale': 50}, {'t': 'save'}]
        t0 = time.time()
        ok = with_retry(ops, 'b3_%d' % k)
        print(T['mark'], 'OK' if ok else 'FAILED', '%.0fs' % (time.time() - t0), flush=True)
        info['hoop'] = T['hoop']; res[T['mark']] = info
        json.dump(res, open(mb.S + r'\w\colinfo_b3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
