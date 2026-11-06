# generate all rigel sheets in batches; AutoCAD relaunched between batches (long sessions crash), file backed up after each batch
import sys, json, os, time, subprocess, shutil, prep, b4rig, gx
DWG = r'D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Б4.ригели.dwg'
NET = os.path.join(gx.S, 'net'); JD = os.path.join(os.environ['TEMP'], 'acadjob_b4')
BK = os.path.join(gx.S, 'w', 'bk')
os.makedirs(BK, exist_ok=True)


def ps(cmd):
    return subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def start():
    for f in ('listening.txt', 'done.txt', 'job.txt'):
        try: os.remove(os.path.join(JD, f))
        except OSError: pass
    pid = ps('$p=Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList \'"%s" /nologo /b "%s"\' -PassThru; $p.Id' % (DWG, os.path.join(NET, 'boot.scr'))).strip()
    for i in range(200):
        if os.path.exists(os.path.join(JD, 'listening.txt')): break
        time.sleep(2)
    else:
        raise RuntimeError('listener did not start')
    return pid


def stop(pid):
    gx.run([dict(t='save')], 'sv')
    ps('Stop-Process -Id %s -Force' % pid); time.sleep(3)
    shutil.copy(DWG, os.path.join(BK, 'b4_%s.dwg' % time.strftime('%H%M%S')))


marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
first = sys.argv[1] if len(sys.argv) > 1 else '6.1'
todo = sh[[p['no'] for _, p in sh].index(first):]
B = 12
pid = start()
if first == '6.1':
    gx.run([dict(t='eraseregion', win=[170000, 419990, 172179 + 31500 * 80, 434860])], 'clr')
    print('cleared', flush=True)
for i, (M, p) in enumerate(todo):
    if i and i % B == 0:
        stop(pid); pid = start(); print('restart', flush=True)
    t0 = time.time()
    try:
        log = b4rig.run(M, p)
        gx.run([dict(t='save')], 'sv')
        print(p['no'], M['mark'], round(time.time() - t0), [l for l in log if 'ERR' in l][:2], flush=True)
    except Exception as ex:
        print(p['no'], M['mark'], 'EXC', ex, flush=True)
stop(pid)
print('ALLDONE', flush=True)
