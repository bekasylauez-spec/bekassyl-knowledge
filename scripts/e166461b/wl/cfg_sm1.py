# См-1: axis А/1 (y = 0), pieces 1100 / 800+250+800 / 800+250+800 / 1100; elevation axis 1 at sheet x 9810
VERT = dict(SX=823500.0, OLDSX=889400.0, AX1=9810.0, L=[15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497],
            PIECES=[(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)],
            LIRA=[(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)],
            ENDS=[(False, True), (True, True), (True, True), (True, False)],
            PLANE=['y', 0], AXES=[9810, 16610, 23060, 29860],
            CHAIN_X=[-125, 5875, 12325, 18825], CHAIN_DIAG=[False, True, True, True], CHAIN_SIDE='LLLL',
            NOTE_SIDE='RRRR', OPEN_R=[True, True, True, False], ZMIN=-4.2, ANALOG_NOTES=True,
            OUT='wl/sm1_vert.json')
SPEC = dict(SP='141248', ST='1415ED', JSONS=['wl/sm1_vert.json', 'wl/sm1_hor.json'], TOTAL_ROW=1, CONC_OFF=2, CONC=30.7102,
            HOOPS=[('Х1*', 8, 930, 230), ('Х2*', 8, 980, 1380), ('Х3*', 8, 830, 460)])
