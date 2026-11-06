# Рм marks on the scheme «Схема каркас БДМ Блок 4.dwg» (sheets 2.2 −0.050, 2.3 +4.500, 2.4 +7.000): SPDS position note
# cloned from the rigel kit (analog pos note, one leader), arrow on the beam edge, shelf 600 off the beam, scale 100.
import json, os, subprocess, gx, prep
SCH = r'D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Схема каркас БДМ Блок 4.dwg'
DOC = 'Схема каркас БДМ Блок 4.dwg'
RIG = r'D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Б4.ригели.dwg'
K = json.load(open(os.path.join(gx.S, 'w', 'k65.json'), encoding='utf-8'))
NOTE = K['A5:4274A9']['h']                     # analog position note «2 (ф25)», one leader
OX = {-0.05: 84100.0, 4.5: 168200.0, 7.0: 252300.0}
AXX = [0, 650, 6650, 12650, 18650, 24850, 31850, 38850, 44850]; AXY = [0, 9000, 13900, 21000, 27500, 36000, 39000]


def run(ops, name):
    p = os.path.join(gx.S, 'ops', name + '.json'); json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(gx.S, 'net', 'job.ps1'), '-Ops', p, '-Doc', DOC], capture_output=True)
    return r.stdout.decode('utf-8', 'replace')


def P(z, x, y): return [OX[z] + 145817.0 + x, -1786760.0 + y]


if __name__ == '__main__':
    print(gx.run([dict(t='opendoc', file=SCH)], 'od')[-300:])
    marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
    ops = [dict(t='import', file=RIG, h=[NOTE], base=[0, 0], to=[0, 0], pre='SRC:')]
    n = 0
    for M in marks:
        z = M['z']; b = M['b']
        for r in M['runs']:
            a, e, c = r['a'], r['e'], r['c']
            axes = AXX if M['dir'] == 'X' else AXY
            u = (a + e) / 2.0
            for k in range(8):                                  # away from axes / column nodes
                if all(abs(u - q) > 900 for q in axes): break
                u += 700 if k % 2 == 0 else -1400
            if M['dir'] == 'X':
                arrow = P(z, u, c + b / 2.0); shelf = P(z, u + 300, c + b / 2.0 + 600)
            else:
                arrow = P(z, c + b / 2.0, u); shelf = P(z, c + b / 2.0 + 600, u + 300)
            n += 1; t = 'SM%d' % n
            ops += [dict(t='clone', h='SRC:' + NOTE, tag=t), dict(t='mcset', h=t, set={'Scale': 100}),
                    dict(t='spmove', h=t, items=[[0] + shelf, [1] + arrow]),
                    dict(t='mcset', h=t, set={'FirstLine': M['mark'], 'SecondLine': ''})]
    ops += [dict(t='erase', h=['SRC:' + NOTE]), dict(t='save')]
    out = run(ops, 'smarks')
    print(n, 'marks', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:5])
