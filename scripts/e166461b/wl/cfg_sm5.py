# См-5: core top wall y = 17650..17900, 7050..10400 (3350, -4.650...+21.450) = analog См-4 geometry; reinforcement from LIRA plane y=17600
L = [9373, 13923, 17973, 21123, 24273, 27423, 30573, 33723, 35473]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7, 21.45]
VERT = dict(SX=1637700.0, AX1=3109.0, L=L, LEV=LEV, G=[(0, 1), (1, 3), (3, 5), (5, 8)], PIECES=[(7050, 10400)], LIRA=[(6800, 10400)],
            ENDS=[(False, False)], PLANE=['y', 17600], AXES=[9909, 13634], CHAIN_X=[7050], CHAIN_DIAG=[False], ZMIN=-4.2, ANALOG_NOTES=True,
            OUT='wl/sm5_vert.json')
HOR = dict(SX=1637700.0, L=L, LEV=LEV, PLANE=['y', 17600], LIRA=[(6800, 10400)], AXES=[27074, 30799], P0=0, CK0=0, VJSON='wl/sm5_vert.json',
           STRAIGHT=3310, NPAIR=1, XE=30904.0, XD=32068.0, OUT='wl/sm5_hor.json')
