import sys, os, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/lira')
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/lira')
import rdesign as R
M = json.load(open('marks.json', encoding='utf-8'))
G = pickle.load(open('groups_u.pkl', 'rb'))
# map marks to groups by order of runs
out = []; tot_out = tot_in = 0
for D, g in zip(M, G):
    rs = g[1] if isinstance(g, tuple) else g
    P = R.env(rs)
    sup = lambda u: any(a + 1 < u < e - 1 for a, e, _ in D['sups'])
    w_out = 0; w_in = 0; mt = mb = 0; mtin = mbin = 0
    for u, bo, to, w in P:
        At = D['Asm'] + sum(d['n'] * R.A28 for d in D['dops'] if d['top'] and d['a'] <= u <= d['b'])
        Ab = D['Asm'] + sum(d['n'] * R.A28 for d in D['dops'] if not d['top'] and d['a'] <= u <= d['b'])
        if sup(u):
            mtin = max(mtin, to); mbin = max(mbin, bo)
            if to > At + .05 or bo > Ab + .05: w_in += 1
        else:
            mt = max(mt, to - At); mb = max(mb, bo - Ab)
            if to > At + .05 or bo > Ab + .05: w_out += 1
    tot_out += w_out; tot_in += w_in
    out.append((D['mark'], D['count'], len(rs), D['Asm'], round(D['top_req'],1), round(D['bot_req'],1), round(mtin,1), round(mbin,1), w_out, w_in, D['nbad']))
for o in out: print(*o, sep='|')
print('TOTAL span-viol', tot_out, 'inside-support viol', tot_in, 'pcs', sum(o[1] for o in out))
