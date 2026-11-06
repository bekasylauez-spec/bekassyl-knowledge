import sys, os, json, pickle
H = os.path.dirname(os.path.abspath(__file__)) + '/lira'; sys.path.insert(0, H); os.chdir(H)
import rdesign as R
M = json.load(open('marks.json', encoding='utf-8')); G = pickle.load(open('groups_u.pkl', 'rb'))
for D, g in zip(M, G):
    rs = g[1] if isinstance(g, tuple) else g
    worst = None
    for u, bo, to, w in R.env(rs):
        if not any(a + 1 < u < e - 1 for a, e, _ in D['sups']): continue
        At = D['Asm'] + sum(d['n'] * R.A28 for d in D['dops'] if d['top'] and d['a'] <= u <= d['b'])
        Ab = D['Asm'] + sum(d['n'] * R.A28 for d in D['dops'] if not d['top'] and d['a'] <= u <= d['b'])
        for k, req, pr in (('верх', to, At), ('низ', bo, Ab)):
            if req > pr + .05 and (worst is None or req - pr > worst[3] - worst[4]): worst = (k, round(u), D['sups'], round(req,1), round(pr,1))
    if worst:
        k,u,s,req,pr = worst
        print(D['mark'], k, 'u=%d'%u, 'треб %.1f есть %.1f (%+.0f%%)'%(req,pr,(req/pr-1)*100), 'доп:', [(d['top'],d['a'],d['b'],d['n']) for d in D['dops']][:6])
