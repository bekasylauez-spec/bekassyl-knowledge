# См-6: axis В (y = 22750), corner piers only 125..1225 and 18825..19925 (scheme 2.1/2.2), -4.650...+19.700; analog См-5 (4.16/4.17)
L = [15206, 19756, 23806, 26956, 30106, 33256, 36406, 39556]
VERT = dict(SX=1786200.0, AX1=9701.0, L=L,
            PIECES=[(125, 1225), (18825, 19925)], LIRA=[(0, 1225), (18825, 20050)],
            ENDS=[(False, True), (True, False)], PLANE=['y', 22750], AXES=[9701, 16501, 22951, 29751],
            CHAIN_X=[-125, 18825], CHAIN_DIAG=[False, True], CHAIN_SIDE='LL', NOTE_SIDE='RR', OPEN_R=[True, False],
            ZMIN=-4.2, ANALOG_NOTES=True, CHAIN_FORCE='LL', OUT='wl/sm6_vert.json')
