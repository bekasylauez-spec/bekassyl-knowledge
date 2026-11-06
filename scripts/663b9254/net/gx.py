import json, subprocess, os, sys
S = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\663b9254-0821-4243-aa62-da5f6760d929\scratchpad"
DOC = "Б3.колонны.dwg"
def run(ops, name='ops', doc=None):
    p = os.path.join(S, 'ops', name + '.json')
    json.dump(ops, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 'net', 'job.ps1'), '-Ops', p, '-Doc', doc or DOC], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'], 'k3_map.json'), encoding='utf-8-sig'))
def log():
    return open(os.path.join(os.environ['TEMP'], 'k3_log.txt'), encoding='utf-8').read()
if __name__ == '__main__':
    print(run(json.load(open(sys.argv[1], encoding='utf-8')), 'cli'))
