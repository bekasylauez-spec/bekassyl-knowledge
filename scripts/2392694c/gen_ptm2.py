# 7.41 ПтМ-2 from analog 6.3: box 3100x7650 equals ours (stair box 10275..13375 x 15225..22875, axis 3 = right wall,
# axis Б 475 below the box). Axes 2/Б1 of the analog do not exist here -> removed, 2/1 -> 3, binding dims redone,
# section mark moved onto the wall of axis 3, levels +21.500/+22.200 -> +22.400/+23.100, texts.
import gx
S = 2448879.0
ops = [
    {'t': 'axis', 'h': '33A2F8', 'val': '3'}, {'t': 'axis', 'h': '344F7E', 'val': '3'},
    {'t': 'axis', 'h': '33A0BE', 'val': '3'}, {'t': 'axis', 'h': '33A0F9', 'val': '3'},
    {'t': 'erase', 'h': ['33A2E8', '33A2F9', '33A307', '33A308', '33A33A', '33A34C', '33A37C', '33A38E', '344F7C', '344F7F', '344F7D']},
    # opalubka 1:100: 2975 left face -> axis 3, Б -> В 8000, 475 Б -> box
    {'t': 'dimpts', 'h': '33A309', 'p1': [2459796, 478367, 0], 'p2': [2462771, 478367, 0], 'dl': [2459796, 477405, 0]},
    {'t': 'dimpts', 'h': '33A2FA', 'p1': [2459408, 487544, 0], 'p2': [2459408, 479544, 0], 'dl': [2457408, 487544, 0]},
    {'t': 'clone', 'h': '33A3C1', 'tag': 'P41_475'},
    {'t': 'dimpts', 'h': 'P41_475', 'p1': [2462896, 479544, 0], 'p2': [2462896, 480019, 0], 'dl': [2464135, 479544, 0]},
    # armirovanie 1:50 (x2)
    {'t': 'dimpts', 'h': '344F81', 'p1': [2477635, 474357, 0], 'p2': [2483585, 471053, 0], 'dl': [2477635, 470803, 0]},
    {'t': 'dimpts', 'h': '344F80', 'p1': [2476860, 489407, 0], 'p2': [2476860, 473407, 0], 'dl': [2473660, 489407, 0]},
    # section mark 1-1 across the wall of axis 3
    {'t': 'secset', 'h': '33A2E5', 'word': '1', 'pts': [[2463900, 486225], [2461900, 486225]]},
    {'t': 'levelval', 'h': '33A0BA', 'old': '+21,500', 'value': '+22,400'}, {'t': 'levelval', 'h': '33A102', 'old': '+21,500', 'value': '+22,400'},
    {'t': 'levelval', 'h': '33A0BD', 'old': '+22,200', 'value': '+23,100'}, {'t': 'levelval', 'h': '33A132', 'old': '+22,200', 'value': '+23,100'},
    {'t': 'trepl', 'win': [S, 455900, S + 59400, 498000], 'pairs': [['КЖ-6.3', 'КЖ-7.37 ... 7.41'], ['+22.200', '+23.100'], ['+21.500', '+22.400']]},
    {'t': 'save'}]
out = gx.run(ops, 'p41')
print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'AXIS' in l or 'level' in l.lower() or 'trepl' in l or 'secset' in l))
