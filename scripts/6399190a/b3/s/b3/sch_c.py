import json, sys
sys.path.insert(0, r'..\t'); import mb
from sch_a import P, HP
ops = []
def add(**k): ops.append(k)
# stair dims right of axis 22
add(t='dim', h='B3BD1', p1=P(136300, 0), p2=P(136300, 3150), dl=P(139300, 0), rot=HP, tag='B3BS1')
add(t='dim', h='B3BD1', p1=P(136300, 3150), p2=P(136300, 5800), dl=P(139300, 0), rot=HP, tag='B3BS2')
# 150 (В/21-22) and 2500 (upper columns) dims to the left, clear of mark leaders
add(t='erase', h=['B3BD24', 'B3BD25', 'B3BD26'])
add(t='dim', h='B3BD1', p1=P(133050, 10500), p2=P(133050, 10650), dl=P(132350, 10500), rot=HP, tx=P(132350 - 450, 10650 + 450), tag='B3BS3')
add(t='dim', h='B3BD1', p1=P(112300, 10500), p2=P(112300, 13000), dl=P(111200, 10500), rot=HP, tag='B3BS4')
add(t='dim', h='B3BD1', p1=P(112300, 21000), p2=P(112300, 23500), dl=P(111200, 21000), rot=HP, tag='B3BS5')
add(t='save')
print(mb.run(ops, 'sch_c', 600)[-500:])
