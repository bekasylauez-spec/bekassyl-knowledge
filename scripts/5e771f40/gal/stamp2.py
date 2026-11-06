# Galaxy stamp (TUNAY STROY block) -> customer stamp «Штамп_АБК» (АБК Завод, same customer), name field -> Маслоподготовка Блок 2
import os, gx
SRC = os.path.join(gx.S, '..', 'an', 'abk.dwg'); H = '3831F6'; BASE = [-427003.00094608066, -1748922.0]
BLK = 'Штамп_МП3'


def stamp(p):
    P = p['P']; cx, cy = p['SX'] + 31250, p['SY'] + 250
    ops = [dict(t='import', file=os.path.abspath(SRC), h=[H], base=BASE, to=[cx, cy], pre=P + '_ST:'),
           dict(t='blkcopy', src='Штамп_АБК', name=BLK, repl={'АБК': 'Маслоподготовка. Блок 3'}),
           dict(t='setblock', h=P + '_ST:' + H, name=BLK),
           dict(t='erase', h=[P + ':40443F']),
           dict(t='moveto', h=P + ':404440', idx=0, to=[cx - 1375, cy + 1000]),
           dict(t='moveto', h=P + ':404442', idx=0, to=[cx - 4250, cy + 375])]
    return gx.run(ops, 'st' + P)
