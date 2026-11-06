import json, subprocess, os, sys
S=r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad"
def run(ops, name='ops', doc=None, wait=900):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p,'-Wait',str(wait)]+(['-Doc',doc] if doc else []),capture_output=True)
    return r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'b1_map.json'),encoding='utf-8-sig'))
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))


def restart_acad():
    """kill my AutoCAD (pid in net/pid.txt) and start it again with the boot script (listener + working DWG)"""
    import time
    pf = os.path.join(S, 'net', 'pid.txt')
    try:
        pid = int(open(pf).read().strip())
        subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
    except Exception:
        pass
    time.sleep(3)
    jd = os.path.join(os.environ['TEMP'], 'acadjob_b1')
    for f in ('job.txt', 'done.txt', 'listening.txt'):
        try: os.remove(os.path.join(jd, f))
        except Exception: pass
    for f in ('Б1.ригели.dwl', 'Б1.ригели.dwl2'):
        try: os.remove(os.path.join(r'D:\РАБОЧКА\От Шерхан\Бдм Блок 1', f))
        except Exception: pass
    # WMI-created process: not in this runner's process tree -> survives when the runner is stopped
    r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'startacad.ps1')], capture_output=True)
    class _P: pass
    p = _P(); p.pid = int((r.stdout.decode().strip() or '0').splitlines()[-1])
    open(pf, 'w').write(str(p.pid))
    for i in range(150):
        time.sleep(2)
        if os.path.exists(os.path.join(jd, 'listening.txt')): break
    time.sleep(15)
    out = run([dict(t='docinfo')], 'ping', wait=240)
    return p.pid, out
