import subprocess, os, time, gx
S = gx.S
def mypid():
    r = subprocess.run(['powershell', '-Command', "Get-Process acad -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*Б2 Ригели*' } | ForEach-Object { $_.Id }"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return [int(x) for x in r.stdout.split() if x.strip().isdigit()]
def kill():
    for p in mypid(): subprocess.run(['powershell', '-Command', 'Stop-Process -Id %d -Force' % p])
    time.sleep(3)
def restart():
    kill(); subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'restart.ps1')], capture_output=True)
