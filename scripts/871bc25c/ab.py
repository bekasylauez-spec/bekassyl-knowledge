import json, subprocess, os, sys
S = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\871bc25c-1995-48d6-a9cc-b596c8ecdf97\scratchpad"
DWG = r"D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК.dwg"


def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')


def tagmap():
    try:
        return json.load(open(os.path.join(os.environ['TEMP'], 'ab_map.json'), encoding='utf-8-sig'))
    except Exception:
        return {}


def dxf(path=S + r'\w\live.dxf'):
    """DXF of the LIVE db (handles preserved)"""
    if os.path.exists(path):
        os.remove(path)
    out = run([{'t': 'dxfout', 'file': path}], 'dxfout')
    return out


if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
