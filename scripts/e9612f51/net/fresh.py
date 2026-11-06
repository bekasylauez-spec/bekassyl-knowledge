import os, sys, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_all, gx, rigx
def fresh():
    for pid in run_all.my_acad(): subprocess.run(['powershell', '-NoProfile', '-Command', 'Stop-Process -Id %d -Force' % pid])
    import time; time.sleep(4)
    shutil.copy(r'R:\От Шерхан\БДМ Блок 3\Схема каркас БДМ Блок 3.dwg', run_all.DWG)
    p = os.environ['TEMP'] + r'\b3_map.json'
    if os.path.exists(p): os.remove(p)
    run_all.restart()
    hs = [h for h in rigx.handles_in(-212862, 426649, -204462, 432589) if h not in ('407C02', '40647F')]
    out = gx.run([dict(t='import', file=gx.S + r'\an\a61.dwg', h=hs, base=[-212862, 426649], to=[172179, 430000], pre='S1:'),
                  dict(t='import', file=gx.S + r'\an\a61.dwg', h=['42FC64', '4308C2', '42F9FB', '42F9FC'], base=[0, 0], to=[0, 0], pre='B6:'),
                  dict(t='save')], 'setup')
    return [l for l in out.splitlines() if 'import' in l]
if __name__ == '__main__':
    print(fresh())
