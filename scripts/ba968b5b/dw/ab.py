import json, subprocess, os, sys
S = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\ba968b5b-1d4b-478a-a5fc-898fa1c252b5\scratchpad\dw"
NET = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\ba968b5b-1d4b-478a-a5fc-898fa1c252b5\scratchpad\dw\net"
def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(NET, 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
def tagmap():
    try: return json.load(open(os.path.join(os.environ['TEMP'], 'ab_map.json'), encoding='utf-8-sig'))
    except Exception: return {}
def dxf(path=S + r'\w\live.dxf'):
    if os.path.exists(path): os.remove(path)
    return run([{'t': 'dxfout', 'file': path}], 'dxfout')
if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
