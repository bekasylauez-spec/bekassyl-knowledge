import io, collections, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'D:\_claude_work\zavod_km')
src = io.open('gen_razv2.py', encoding='utf-8-sig').read()
src = src.replace("json.dump(ops, open('D:/_claude_work/zavod_km/job/razv2.json', 'w', encoding='utf-8'), ensure_ascii=False)", "")
src = src.replace("def elevation(X0, G, S):", "def elevation(X0, G, S):\n    REC.append(S)\n    return _elev(X0,G,S)\ndef _elev(X0, G, S):", 1)
ns = {'REC': []}; REC = ns['REC']
exec(compile(src, 'g', 'exec'), ns)
L = collections.defaultdict(float); N = collections.Counter()
for S in REC:
    for a0, v0, a1, v1, mk, vert in S['pieces']:
        ln = abs(v1 - v0) if vert else abs(a1 - a0)
        k = (mk or '(РФ2 без марки)').replace('@L', '')
        L[k] += ln / 1000; N[k] += 1
for k in sorted(L): print(k, N[k], round(L[k], 1), 'm')
print('elevations', len(REC))
