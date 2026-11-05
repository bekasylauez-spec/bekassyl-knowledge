# См-3: y = 13850, stubs 3100 from axis 1 and axis 4 (same as the analog См-3, no stretch); one sheet: vertical left, horizontal right (+30000)
L = [12597, 17147, 21197, 24347, 27497, 30647, 33797, 36947]
VERT = dict(SX=1368200.0, AX1=10944.0, L=L,
            PIECES=[(125, 3225), (9975, 13075)], LIRA=[(0, 3275), (0, 3275)],
            ENDS=[(False, True), (True, False)], LENDS=[(False, True), (False, True)], PLANE=['y', 13875], AXES=[10944, 24144],
            CHAIN_X=[125, 9975], CHAIN_DIAG=[False, False], CHAIN_FORCE='RL', CHAIN_OFF_R=[350, 350],
            ZMIN=-4.2, ANALOG_NOTES=True, OUT='wl/sm3_vert.json')
HOR = dict(SX=1368200.0, L=L, PLANE=['y', 13875], LIRA=[(0, 3275)], AXES=[40944, 54144],
           P0=0, CK0=0, VJSON='wl/sm3_vert.json', STRAIGHT=3310, NPAIR=2, XE=54239.0, XD=55404.0, OUT='wl/sm3_hor.json')
SPEC = dict(SP='17E05E', ST='17E1ED', JSONS=['wl/sm3_vert.json', 'wl/sm3_hor.json'], TOTAL_ROW=1, CONC_OFF=1, CONC=35.0325,
            HOOPS=[('Шп1*', 8, 370, 1170), ('Х1*', 8, 980, 936)])
