# См-2: y = 7550 (between А and Б), pieces 1300+250+1300 at axes 2 and 3; elevation axis 1 at sheet x 8845
VERT = dict(SX=1160300.0, AX1=8845.0, L=[13584, 18134, 22184, 25334, 28484, 31634, 34784, 37934],
            PIECES=[(5375, 6675), (6925, 8225), (11825, 13125), (13375, 14675)],
            LIRA=[(5375, 6675), (6925, 8225), (11700, 13125), (13375, 15375)],
            ENDS=[(True, False), (False, True), (True, False), (False, True)],
            PLANE=['y', 8000], AXES=[8845, 15645, 22095, 28895],
            CHAIN_X=[5375, 8225 + 1400, 11825, 14675 + 1400], CHAIN_DIAG=[True, True, True, True],
            CHAIN_SIDE='LRLR', CHAIN_SKIP=[1, 2], NOTE_LOW=[2], ZMIN=-4.2,              # the foundation-joint cell row is covered by the Фм выпуски
            OUT='wl/sm2_vert.json')
HOR = dict(SX=1219700.0, L=[13584, 18134, 22184, 25334, 28484, 31634, 34784, 37934],
           PLANE=['y', 8000], LIRA=[(5375, 8225), (11700, 15375)], AXES=[8845, 15645, 22095, 28895],
           P0=12, CK0=2, VJSON='wl/sm2_vert.json', STRAIGHT=2850 - 40, NPAIR=2, XE=29000.0, XD=30165.0, OUT='wl/sm2_hor.json')
SPEC = dict(SP='156C91', ST='156F9D', JSONS=['wl/sm2_vert.json', 'wl/sm2_hor.json'], TOTAL_ROW=1, CONC_OFF=1,
            CONC=28.68 * 5200 / 5075)          # analog pieces 1275+1100+1425+1275 -> ours 4 x 1300
