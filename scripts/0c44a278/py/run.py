import json, subprocess, os, sys
S = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad"
TMP = os.environ['TEMP']
EXE = r"C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"

def run(ops, dwg_in, dwg_out=None, name='ops', mapfile=None, timeout=1500):
    ops = list(ops)
    if dwg_out:
        ops.append({'t': 'saveas', 'file': dwg_out})
    logf = os.path.join(S, 'w', 'log_%s.txt' % name)
    root = {'ops': ops, 'log': logf, 'map': mapfile or os.path.join(S, 'w', 'map.json')}
    json.dump(root, open(os.path.join(TMP, 'bk_ops.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(root, open(os.path.join(S, 'w', 'ops_%s.json' % name), 'w', encoding='utf-8'), ensure_ascii=False)
    scr = os.path.join(S, 'w', 'run_%s.scr' % name)
    open(scr, 'w', encoding='cp1251').write('_.SECURELOAD\n0\n_.NETLOAD\n"%s"\nBKOPS\n_.QUIT\n_Y\n' % os.path.join(S, 'net', 'bk.dll'))
    if os.path.exists(logf): os.remove(logf)
    r = subprocess.run([EXE, '/i', dwg_in, '/s', scr, '/l', 'ru-RU'], capture_output=True, timeout=timeout)
    out = open(logf, encoding='utf-8').read() if os.path.exists(logf) else ('NO LOG\n' + r.stdout.decode('utf-16', 'replace')[-3000:])
    return out

if __name__ == '__main__':
    ops = json.load(open(sys.argv[1], encoding='utf-8'))
    print(run(ops, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, 'cli'))
