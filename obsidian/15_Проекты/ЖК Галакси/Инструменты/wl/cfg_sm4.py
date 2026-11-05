# См-4: y = 15100..15350. Piece A (core 7050..10400, to +21.450) = analog См-4 unchanged (Bekassyl: «аналогтікін қалдыр»);
# piece B (stair 11750..13250, free left end, to +19.700) from LIRA plane y=15225, drawn right of A (axis 3), numbering after the analog.
L = [9373, 13923, 17973, 21123, 24273, 27423, 30573, 33723]
VERT = dict(SX=1489200.0, AX1=3109.0, L=L, PIECES=[(11750, 13250)], LIRA=[(11700, 13250)], ENDS=[(True, False)], LENDS=[(True, False)],
            PLANE=['y', 15225], AXES=[9909, 16359], CHAIN_X=[11750], CHAIN_DIAG=[False], CHAIN_FORCE='L', CHAIN_OFF_R=[350],
            ZMIN=-4.2, ANALOG_NOTES=True, P0=9, CK0=2, XLO=13900, OUT='wl/sm4_vert.json')
HOR = dict(SX=1489200.0, L=L, PLANE=['y', 15225], LIRA=[(11700, 13250)], AXES=[30074, 36524], XLO=34100,
           P0=0, CK0=0, VJSON='wl/sm4_vert.json', P0X=9, STRAIGHT=1710, NPAIR=1, XE=36744.0, XD=37909.0, OUT='wl/sm4_hor.json')
