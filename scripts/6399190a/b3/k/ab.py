import json, subprocess, os, sys
S = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k"
DWG = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w\m3col.dwg"
def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
def log():
    return open(os.path.join(os.environ['TEMP'], 'm3t_log.txt'), encoding='utf-8').read()
def tagmap():
    try: return json.load(open(os.path.join(os.environ['TEMP'], 'm3t_map.json'), encoding='utf-8-sig'))
    except Exception: return {}
if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
