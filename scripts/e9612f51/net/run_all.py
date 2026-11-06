# generate sheets sh_<a..b>.json one by one in my own AutoCAD; restart AutoCAD every N sheets (eAtMaxReaders / heap crashes)
import subprocess, sys, os, time, json
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.path.join(S, 'net'); W = os.path.join(S, 'w')
DWG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'w', 'b3w.dwg')
JD = os.path.join(os.environ['TEMP'], 'acadjob_b3')
LOG = os.path.join(W, 'run_all.log')
def log(*a):
    with open(LOG, 'a', encoding='utf-8') as f: f.write(time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a) + '\n')

def my_acad():
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"Name='acad.exe'\" | ? { $_.CommandLine -like '*e9612f51*b3w.dwg*' } | % { $_.ProcessId }"], capture_output=True, text=True).stdout.split()
    return [int(x) for x in out]

def restart():
    import gx
    for pid in my_acad():
        try: gx.run([dict(t='save')], 'presave')
        except Exception: pass
    for pid in my_acad():
        subprocess.run(['powershell', '-NoProfile', '-Command', 'Stop-Process -Id %d -Force' % pid])
    time.sleep(4)
    try:
        import shutil; sys.path.insert(0, W); import bis
        shutil.copy(DWG, os.path.join(W, 'snap.dwg'))
        log('integrity', bis.tryplot('integ', [], [172179, 430000, 180579, 435940]))
    except Exception as ex: log('integrity EXC', repr(ex)[:200])
    for ext in ('.dwl', '.dwl2'):
        try: os.remove(DWG[:-4] + ext)
        except OSError: pass
    for f in ('listening.txt', 'job.txt', 'done.txt'):
        try: os.remove(os.path.join(JD, f))
        except OSError: pass
    subprocess.Popen([r'C:\Program Files\Autodesk\AutoCAD 2021\acad.exe', DWG, '/nologo', '/b', os.path.join(NET, 'boot_b3.scr')])
    t0 = time.time()
    while time.time() - t0 < 300 and not os.path.exists(os.path.join(JD, 'listening.txt')):
        time.sleep(5)
        close_proxy_dialog()
    time.sleep(5); close_proxy_dialog()
    log('restart', my_acad(), os.path.exists(os.path.join(JD, 'listening.txt')))

def close_proxy_dialog():
    ps = r'''Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class WQ { public delegate bool EP(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
public static void C(uint pid){ EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)){ var s=new StringBuilder(256); GetWindowText(h,s,256); if(s.ToString().Contains("прокси")) PostMessage(h,0x10,IntPtr.Zero,IntPtr.Zero);} return true;},IntPtr.Zero); } }
"@
Get-Process acad -ErrorAction SilentlyContinue | % { [WQ]::C([uint32]$_.Id) }'''
    subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True)

def integ(tag):
    import gx, shutil
    sys.path.insert(0, W); import bis
    gx.run([dict(t='save')], 'isave')
    shutil.copy(DWG, os.path.join(W, 'snap.dwg'))
    ok = bis.tryplot('integ', [], [172179, 430000, 180579, 435940]); log('integrity', tag, ok); return ok

def sheet(k):
    import wipe
    B = json.load(open(os.path.join(W, 'sh_%d.json' % k), encoding='utf-8'))
    o, n = wipe.wipe(B['P']); log('wipe', k, n)
    r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(NET, 'rb3.py'), os.path.join(W, 'sh_%d.json' % k), '--import', '--run'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1500, cwd=NET)
    out = [l for l in r.stdout.splitlines() if l.strip()]
    log('sheet', k, B['mark'], out[-4:] if out else r.stderr[-400:])
    return all('errors 0' in l for l in out if l.startswith(('geom', 'sec+text', 'tables'))) and len(out) >= 4

def keep_good():
    import shutil
    shutil.copy(DWG, DWG[:-4] + '_good.dwg'); shutil.copy(os.path.join(os.environ['TEMP'], 'b3_map.json'), DWG[:-4] + '_good_map.json')

def restore_good():
    import shutil
    for pid in my_acad(): subprocess.run(['powershell', '-NoProfile', '-Command', 'Stop-Process -Id %d -Force' % pid])
    time.sleep(4)
    shutil.copy(DWG[:-4] + '_good.dwg', DWG); shutil.copy(DWG[:-4] + '_good_map.json', os.path.join(os.environ['TEMP'], 'b3_map.json'))
    log('restored good copy')
    restart()

if __name__ == '__main__':
    a, b = int(sys.argv[1]), int(sys.argv[2])
    sys.path.insert(0, NET); os.chdir(NET)
    keep_good()
    k = a; tries = 0
    while k <= b:
        ok = False
        try: ok = sheet(k)
        except Exception as ex: log('EXC', k, repr(ex)[:300])
        good = ok and integ(k)
        log('RESULT', k, 'OK' if good else 'FAIL')
        if good:
            keep_good(); k += 1; tries = 0
            if (k - a) % 2 == 0: restart()
        else:
            tries += 1
            if tries > 3: log('GIVE UP', k); break
            restore_good()
    log('ALL DONE', a, b)
