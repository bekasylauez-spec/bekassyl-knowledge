import json, subprocess, os, sys
S = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\05b51b6c-d250-4c38-a2d9-9fecb50bf6e5\scratchpad"
DWG = r"D:\РАБОЧКА\От Маке\Завод\Обезвоживание\КЖ Помещение обезвоживания.dwg"


def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    out = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    try:
        out += '\n' + open(os.path.join(os.environ['TEMP'], 'ob_log.txt'), encoding='utf-8').read()
    except Exception:
        pass
    return out


def tagmap():
    try:
        return json.load(open(os.path.join(os.environ['TEMP'], 'ob_map.json'), encoding='utf-8-sig'))
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
