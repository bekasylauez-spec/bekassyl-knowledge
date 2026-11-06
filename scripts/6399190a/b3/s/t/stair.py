import ab, work, ext, plan
def profile(sx, sy):
    L = lambda x, y: [sx + x, sy + y]
    pts = [L(17501, 12218), L(17201, 12218)]
    x, y = 17201, 12218
    for i in range(21):
        pts.append(L(x, y - 150)); x -= 250; y -= 150; pts.append(L(x, y))
    pts += [L(11951, 8918), L(12336, 8918), L(17507, 12018), L(17501, 12018)]
    return pts
def concrete_ops(s, H):
    """H: dict role->handle for this sheet (same layout as analog 8.1/8.2)"""
    sx, sy = work.loc(s, 0, 0)
    L = lambda x, y: [sx + x, sy + y]
    P = profile(sx, sy)
    ops = [{'t': 'erase', 'h': H['treads_del']},
           {'t': 'stretch', 'win': L(7150, 6000) + L(8000, 13500), 'd': [-750, 0]},
           {'t': 'move', 'h': [H['ax_plan2']], 'd': [1900, 0]},
           {'t': 'plset', 'h': H['prof'], 'p': P, 'closed': True},
           {'t': 'hatchset', 'h': H['prof_h'], 'loops': [P]},
           {'t': 'stretch', 'win': L(17900, 12300) + L(19500, 13500), 'd': [-750, -500]},
           {'t': 'stretch', 'win': L(10000, 12300) + L(11050, 13500), 'd': [0, -500]},
           {'t': 'stretch', 'win': L(18700, 8000) + L(19200, 9000), 'd': [-750, 0]},
           {'t': 'hatchset', 'h': H['floor_h'], 'loops': [[L(10951, 8718), L(18201, 8718), L(18201, 8918), L(10951, 8918)]]},
           {'t': 'dimtext', 'h': H['d_flight'], 's': '250х12=3000'},
           {'t': 'dimtext', 'h': H['d_run'], 's': '250х21=5250'},
           {'t': 'dimtext', 'h': H['d_rise'], 's': '150х22=3300'},
           {'t': 'axisval', 'h': H['ax_plan1'], 'val': '9'}, {'t': 'axisval', 'h': H['ax_plan2'], 'val': '10'},
           {'t': 'axisval', 'h': H['ax_sec'], 'val': '10'}]
    return ops
def dimfix_ops(s, H):
    sx, sy = work.loc(s, 0, 0)
    es = {e.h: e for e in plan.dump(work.win(s), 'st' + s.replace('.', ''))}
    ops = []
    for h, a, b in ((H['d_tot'], 2965, 8965), (H['d_mid'], 4165, 7165), (H['d_end'], 7165, 8965)):
        d = es[h].dimpts()
        ops.append({'t': 'dimpts', 'h': h, 'p1': [sx + a, d[0][1]], 'p2': [sx + b, d[1][1]], 'dl': [sx + (a + b) / 2, d[2][1]]})
    return ops
