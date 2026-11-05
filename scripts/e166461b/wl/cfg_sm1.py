# См-1: axis А/1 (y = 0), pieces 1100 / 800+250+800 / 800+250+800 / 1100; elevation axis 1 at sheet x 9810
VERT = dict(SX=889400.0, AX1=9810.0, L=[15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497],
            PIECES=[(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)],
            LIRA=[(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)],
            ENDS=[(False, True), (True, True), (True, True), (True, False)],
            PLANE=['y', 0], AXES=[9810, 16610, 23060, 29860],
            CHAIN_X=[-125, 5875, 12325, 18825], CHAIN_DIAG=[False, True, True, True], CHAIN_SIDE='LLLL',
            NOTE_SIDE='RRRR', OPEN_R=[True, True, True, False], ZMIN=-4.2,
            OUT='wl/sm1_vert.json')
