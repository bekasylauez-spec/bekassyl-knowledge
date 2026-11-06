# generate all rigel sheets in batches; AutoCAD relaunched between batches (long sessions crash), file backed up after each batch
import sys, json, os, time, subprocess, shutil, prep, b4rig, gx
DWG = r'D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Б4.ригели.dwg'
NET = os.path.join(gx.S, 'net'); JD = os.path.join(os.environ['TEMP'], 'acadjob_b4')
BK = os.path.join(gx.S, 'w', 'bk')
os.makedirs(BK, exist_ok=True)


def ps(cmd):
    return subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def start():
    out = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(NET, 'start.ps1')], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    if not os.path.exists(os.path.join(JD, 'listening.txt')): raise RuntimeError('listener did not start ' + out[-300:])
    return out.strip().splitlines()[-1]


def stop(pid):
    gx.run([dict(t='save')], 'sv')
    ps('Stop-Process -Id %s -Force' % pid); time.sleep(3)
    shutil.copy(DWG, os.path.join(BK, 'b4_%s.dwg' % time.strftime('%H%M%S')))


marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
first = sys.argv[1] if len(sys.argv) > 1 else '6.1'
only = [a for a in sys.argv[3:]]
todo = [q for q in sh if q[1]['no'] in only] if only else sh[[p['no'] for _, p in sh].index(first):]
B = 12
pid = sys.argv[2] if len(sys.argv) > 2 else start()
if first == '6.1' and not only:
    gx.run([dict(t='eraseregion', win=[170000, 419990, 172179 + 31500 * 80, 434860])], 'clr')
    print('cleared', flush=True)
for i, (M, p) in enumerate(todo):
    if i and i % B == 0:
        stop(pid); pid = start(); print('restart', flush=True)
    for attempt in range(3):
        t0 = time.time()
        try:
            log = b4rig.run(M, p)
            hung = any('timeout' in l for l in log)
            if not hung:
                out = gx.run([dict(t='save')], 'sv'); hung = 'timeout' in out
            if hung: raise TimeoutError('AutoCAD did not answer')
            print(p['no'], M['mark'], round(time.time() - t0), [l for l in log if 'ERR' in l][:2], flush=True)
            break
        except Exception as ex:
            print(p['no'], M['mark'], 'EXC', ex, '-> restart AutoCAD', flush=True)
            ps('Stop-Process -Id %s -Force' % pid); time.sleep(3)
            pid = start(); print('restart after hang', flush=True)
stop(pid)
print('ALLDONE', flush=True)
