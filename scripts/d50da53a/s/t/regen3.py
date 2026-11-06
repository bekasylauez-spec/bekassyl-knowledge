# robust driver: per type run chunks; on AutoCAD hang (timeout) restart instance and redo the type
import sys, json, time, subprocess, os
import mb, gcol
RST = os.path.join(mb.S, 't', 'restart.ps1')
def restart():
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', RST], capture_output=True)
    print('RESTART', r.stdout.decode('utf-8', 'replace').strip()[-60:], flush=True)
    mb.run([{'t': 'sysvar', 'n': 'SAVETIME', 'v': 0}], 'sv', 120)

def run_ops(ops, name, CH=80, wait=180):
    i = 0
    while i < len(ops):
        t0 = time.time(); out = mb.run(ops[i:i + CH], '%s_%d' % (name, i), wait)
        if 'timeout' in out.splitlines()[0:3].__str__() or 'timeout' in out[:300]:
            print(name, 'TIMEOUT at', i, flush=True); return False
        errs = [l for l in out.splitlines() if 'ERR' in l]
        if errs: print(name, i, errs[:4], flush=True)
        i += CH
    return True

def with_retry(ops, name, tries=3):
    for k in range(tries):
        if run_ops(ops, name): return True
        restart()
    return False

if __name__ == '__main__':
    TY = json.load(open(mb.S + r'\coltypes.json', encoding='utf-8'))
    res = {}
    for k, T in enumerate(TY):
        if sys.argv[1:] and T['mark'] not in sys.argv[1:]: continue
        x0 = gcol.SL0 + k * gcol.SW; y0 = gcol.O0[1]
        lay = '4.%d' % (k + 2)
        ops = [{'t': 'eraseregion', 'win': [x0 - 1, y0 - 3000, x0 + gcol.SW + 1, y0 + 24000]}, {'t': 'laydel', 'name': lay}]
        o, info = gcol.build(T, k, lay); ops += o
        ops += [{'t': 'laycopy', 'src': 'x4.1', 'dst': lay}, {'t': 'vpset2', 'layout': lay, 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [x0, y0, x0 + 29700, y0 + 21000], 'scale': 50}, {'t': 'save'}]
        t0 = time.time()
        ok = with_retry(ops, 'rg%d' % k)
        print(T['mark'], 'OK' if ok else 'FAILED', '%.0fs' % (time.time() - t0), flush=True)
        res[T['mark']] = info
        json.dump(res, open(mb.S + r'\w\colinfo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
