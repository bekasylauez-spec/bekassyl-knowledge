exec(open(r'C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\rmc_nodes.py', encoding='utf-8-sig').read().split("ALL = (-1e4, 1e4)")[0])
import math
from shapely.geometry import box
ALL=(-1e4,1e4)
for hwf, am, ap, title in ((125, 42.34, 45.0, 'B/F y=6000: -y 42.34 (A жаққа), +y 45 (C жаққа)'), (140, 45.0, 43.70, 'C/E y=12000: -y 45, +y 43.70 (жотаға)')):
    mem = [M('Р3', (0, 0), (1, 0), +1, 120, e=30),
           M('ГС +y', (0, 0), (math.cos(math.radians(ap)), math.sin(math.radians(ap))), +1, 80, ti=6, e=25),
           M('ГС -y', (0, 0), (math.cos(math.radians(am)), -math.sin(math.radians(am))), +1, 80, ti=6, e=25)]
    pl = solve0(mem, [(box(-3, -3000, 3, 3000), ALL)], 16, box(-100, -3000, hwf + 5, 3000))
    report(title, pl, 16, [(3, -150), (3, 150)], sup_lines=[((3, -3000), (3, 3000))])
# crossing distances
for nm, a in (('СВ1 5993',22.43),('СВ1 5843',22.95),('СВ2 5993',29.77),('СВ2 5843',30.40),('СВ3',37.37),('СВ4',21.69),('СВ5',20.10)):
    th=2*a; print(nm, 'theta %.1f'%th, 'd_c=%.0f'%(50+90/math.tan(math.radians(th))))
for nm, th in (('ГС 45',90),('ГС 42.34',84.68),('ГС 43.7',87.4)):
    print(nm, 'd_c=%.0f'%(50+60/math.tan(math.radians(th))))

