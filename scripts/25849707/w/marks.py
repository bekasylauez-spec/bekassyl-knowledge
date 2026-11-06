import json, collections
from design import AXX, AXY, axlab
P = json.load(open('pieces.json'))
def sig(r):
    sp = tuple((round(b - a), ) for a, b in r['spans'])
    gaps = tuple(round(r['spans'][i + 1][0] - r['spans'][i][1]) for i in range(len(r['spans']) - 1))
    ends = (round(r['spans'][0][0] - r['endL']), round(r['endR'] - r['spans'][-1][1]), r['colL'], r['colR'])
    dop = lambda k: tuple((z['k'], z['d'], round(z['u0'] - r['endL'], -2), round(z['u1'] - r['u0'] if False else z['u1'] - r['endL'], -2)) for z in r[k]['dop'])
    return (r['b'], r['h'], sp, gaps, ends, r['top']['d'], r['bot']['d'], dop('top'), dop('bot'), r['hoop']['d'])
def sig_rev(r):
    # same beam seen from the other end
    L = r['endR'] - r['endL']
    rr = dict(r); rr['spans'] = [(L - (b - r['endL']) + r['endL'], L - (a - r['endL']) + r['endL']) for a, b in reversed(r['spans'])]
    rr['colL'], rr['colR'] = r['colR'], r['colL']
    for k in ('top', 'bot'):
        rr[k] = dict(r[k]); rr[k]['dop'] = [dict(z, u0=r['endL'] + r['endR'] - z['u1'], u1=r['endL'] + r['endR'] - z['u0']) for z in reversed(r[k]['dop'])]
    return sig(rr)
order = sorted([r for r in P if not r.get('nolira')], key=lambda r: (r['z'], r['d'] == 'Y', r['c'], r['a0']))
marks = []; bysig = {}
for r in order:
    s = sig(r); s2 = sig_rev(r)
    m = bysig.get(s) or bysig.get(s2)
    lab = axlab(r['c'], AXY if r['d'] == 'X' else AXX)
    ax = (AXX if r['d'] == 'X' else AXY)
    def near(u):
        return min(ax, key=lambda p: abs(p[0] - u))
    loc = dict(z=r['z'], d=r['d'], c=r['c'], lab=lab, frm=near(r['endL'])[1], to=near(r['endR'])[1], a0=r['endL'], a1=r['endR'])
    if m is None:
        m = dict(name='Рм-%d' % (len(marks) + 1), r=r, locs=[]); marks.append(m); bysig[s] = m
    m['locs'].append(loc)
json.dump(marks, open('marks.json', 'w'), ensure_ascii=False)
for m in marks:
    r = m['r']
    print('%-6s %4.2f b%dx%d L%5d sp%d  top %dØ%d+%d bot %dØ%d+%d X Ø%d/%d%s x%d  %s' % (m['name'], r['z'], r['b'], r['h'], r['L'], len(r['spans']), r['n'], r['top']['d'], len(r['top']['dop']), r['n'], r['bot']['d'], len(r['bot']['dop']), r['hoop']['d'], r['hoop']['legs'], '' if r['hoop']['ok'] else ' NG', len(m['locs']),
          '; '.join('%s %s(%s-%s)' % (l['d'], l['lab'] or int(l['c']), l['frm'], l['to']) for l in m['locs'])))
print(len(marks))
