import json, subprocess, os, sys
S = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\d50da53a-3ac3-4689-a264-f515b6d8bdb3\scratchpad\s"
DWG = r"D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 2\4.Колонна Блок 2.dwg"
os.makedirs(os.path.join(S, 'ops'), exist_ok=True)


def run(ops, name='ops', wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 't', 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)], capture_output=True)
    out = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    return out


def log():
    return open(os.path.join(os.environ['TEMP'], 'mb2_log.txt'), encoding='utf-8').read()


def tagmap():
    try:
        return json.load(open(os.path.join(os.environ['TEMP'], 'mb2_map.json'), encoding='utf-8-sig'))
    except Exception:
        return {}


if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
