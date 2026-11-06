# all rigel sheets, one listener client; fresh AutoCAD per sheet, good-copy after each sheet
import run3, subprocess, os, sys, time, shutil, gx
S = gx.S
DWG = os.path.join(S, 'w', 'Б2 Ригели.dwg'); GOOD = os.path.join(S, 'w', 'Б2 Ригели_good.dwg')
LOG = open(os.path.join(S, 'w', 'batch.log'), 'a', encoding='utf-8')


def log(m):
    LOG.write(time.strftime('%H:%M:%S ') + m + '\n'); LOG.flush(); print(m, flush=True)


def mypid():
    r = subprocess.run(['powershell', '-Command', "Get-Process acad -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*Б2 Ригели*' } | ForEach-Object { $_.Id }"],
                       capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return [int(x) for x in r.stdout.split() if x.strip().isdigit()]


def kill():
    for p in mypid():
        subprocess.run(['powershell', '-Command', 'Stop-Process -Id %d -Force' % p]); log('killed my acad %d' % p)
    time.sleep(3)


def restart():
    kill()
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'restart.ps1')], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    log('restart: ' + r.stdout.strip()[-80:])


todo = run3.SHEETS
if len(sys.argv) > 1: todo = [x for x in todo if x[0] in sys.argv[1:]]
for mark, pi in todo:
    ok = False
    for attempt in range(3):
        restart()
        try:
            run3.run(mark, pi, log=log); ok = True
        except Exception as e:
            log('EXC %s %d %r' % (mark, pi, e))
            kill()
            if os.path.exists(GOOD): shutil.copy(GOOD, DWG); log('restored good copy')
            continue
        kill()
        shutil.copy(DWG, GOOD)
        break
    if not ok: log('FAILED %s %d' % (mark, pi))
log('batch done')
