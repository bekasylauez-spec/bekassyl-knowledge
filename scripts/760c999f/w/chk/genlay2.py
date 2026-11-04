# keep the user's layouts; only rename / create missing ones. Plot window = sheet frame projected into paper space
# through the layout's main viewport (original dumps lay_<k>.txt); new layouts use [0,0,w,h].
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
C = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk'
keys = sys.argv[1:] or ['g11', 'g12', 'sch', 'fnd', 'vyp', 'col', 'wal', 'rig', 'p71', 'p72', 'st8', 'rmp']
ren = {'g11': [['1.5', '1.1']], 'sch': [[str(i), '2.%d' % i] for i in range(1, 11)], 'fnd': [['3.2.', '3.2'], ['3.7 (2)', '3.8']], 'vyp': [['3.3', '3.12'], ['3.2', '3.11'], ['3.1', '3.10']], 'wal': [['19', '5.19']]}
rebuild = {'g11': ['1.1']}
VP = re.compile(r'\[vp (\w+) c=\(([-\d]+),([-\d]+)\) ([-\d]+)x([-\d]+) vc=\(([-\d]+),([-\d]+)\) vh=([-\d]+) sc=([\d.E+-]+) on=(\w+) tg=\(([-\d]+),([-\d]+)\) tw=([-\d.]+) num=([-\d]+)')
for k in keys:
    J = json.load(open(os.path.join(C, 'pM_' + k, 'plotc.json'), encoding='utf-8-sig'))
    rmap = {a: b for a, b in ren.get(k, [])}
    lay = {}
    for ln in open(os.path.join(C, 'lay_%s.txt' % k), encoding='utf-8-sig'):
        f = ln.rstrip('\n').split('\t')
        if len(f) < 3 or f[2] == 'Model': continue
        lay[rmap.get(f[2], f[2])] = VP.findall(ln)[1:]
    jobs = []; pl = []; pc = []
    od = os.path.join(C, 'pL2_' + k); os.makedirs(od, exist_ok=True)
    for j in J:
        n = j['n']; w, h = j['w'], j['h']; out = os.path.join(od, n + '.pdf')
        if n in rebuild.get(k, []) or n not in lay:
            jobs.append({'n': n, 'x0': j['x0'], 'y0': j['y0'], 'x1': j['x1'], 'y1': j['y1'], 'sc': j['sc'], 'w': w, 'h': h, 'media': j['media']})
            win = [0, 0, w, h]; how = 'NEW'
        else:
            # main viewport = the one covering the frame best
            best = None
            for h_, cx, cy, vw, vh_, vcx, vcy, vh2, sc, on, tgx, tgy, tw, num in lay[n]:
                sc = float(sc); vw = float(vw); vh_ = float(vh_); mcx = float(vcx) + float(tgx); mcy = float(vcy) + float(tgy)
                mw, mh = vw / sc, vh_ / sc; x0, y0, x1, y1 = mcx - mw / 2, mcy - mh / 2, mcx + mw / 2, mcy + mh / 2
                cov = max(0, min(x1, j['x1']) - max(x0, j['x0'])) * max(0, min(y1, j['y1']) - max(y0, j['y0'])) / ((j['x1'] - j['x0']) * (j['y1'] - j['y0']))
                if best is None or cov > best[0]: best = (cov, float(cx), float(cy), mcx, mcy, sc)
            cov, cx, cy, mcx, mcy, sc = best
            if cov < 0.8:
                print('REBUILD', k, n, 'main viewport covers only %.2f of own frame' % cov)
                jobs.append({'n': n, 'x0': j['x0'], 'y0': j['y0'], 'x1': j['x1'], 'y1': j['y1'], 'sc': j['sc'], 'w': w, 'h': h, 'media': j['media']})
                pl.append({'layout': n, 'out': out, 'win': [0, 0, w, h], 'wmedia': j['media']}); pc.append(dict(j, out=out)); continue
            px0 = cx + (j['x0'] - mcx) * sc; py0 = cy + (j['y0'] - mcy) * sc; px1 = cx + (j['x1'] - mcx) * sc; py1 = cy + (j['y1'] - mcy) * sc
            if abs((px1 - px0) - w) > 1 or abs((py1 - py0) - h) > 1: print('WARN', k, n, 'paper window %.0fx%.0f vs format %dx%d' % (px1 - px0, py1 - py0, w, h))
            win = [round(px0, 2), round(py0, 2), round(px1, 2), round(py1, 2)]; how = 'USER'
        pl.append({'layout': n, 'out': out, 'win': win, 'wmedia': j['media']})
        pc.append(dict(j, out=out))
        print(k, n, how, win)
    json.dump({'ren': ren.get(k, []), 'jobs': jobs}, open(os.path.join(C, 'lay2_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(pl, open(os.path.join(od, 'plotl.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(pc, open(os.path.join(od, 'plotc.json'), 'w', encoding='utf-8'), ensure_ascii=False)
