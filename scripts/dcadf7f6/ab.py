import json, subprocess, os, sys
S = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\dcadf7f6-8c14-4657-945c-bf48b0ae9a19\scratchpad"
DWG = r"D:\РАБОЧКА\От Маке\Завод\Аэротенк\КЖ Аэротенк.dwg"
def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
def log():
    return open(os.path.join(os.environ['TEMP'], 'ae_log.txt'), encoding='utf-8').read()
def tagmap():
    try: return json.load(open(os.path.join(os.environ['TEMP'], 'ae_map.json'), encoding='utf-8-sig'))
    except Exception: return {}
if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
