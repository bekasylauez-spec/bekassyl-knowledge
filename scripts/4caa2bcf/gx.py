import json, subprocess, os, sys
S = os.path.dirname(os.path.abspath(__file__))
def run(ops, name='ops', doc=None, wait=900):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Wait', str(wait)] + (['-Doc', doc] if doc else []), capture_output=True)
    return r.stdout.decode('cp866', 'replace') + r.stderr.decode('cp866', 'replace')
def log():
    return open(os.path.join(os.environ['TEMP'], 'b2_log.txt'), encoding='utf-8-sig').read()
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'], 'b2_map.json'), encoding='utf-8-sig'))
if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
