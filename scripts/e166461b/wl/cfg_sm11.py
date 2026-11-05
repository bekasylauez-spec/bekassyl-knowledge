# См-11: axis 4 (x = 20050), analog См-6 «по оси 1 и 4» via the corrected См-7 sheets; floors: [-125..2775], [5750..15675], [20375..22875]
# (openings in piece 2: +3.950 9175..14625 h2200, +7.100...+16.550 windows 6675..7675), basement a full wall. Sheet 5.47 (x 3008100).
L = [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320]
VERT = dict(SX=3008100.0, AX1=15030.0, L=L,
            PIECES=[(125, 2775), (5750, 15675), (20375, 22625)], LIRA=[(0, 2775), (5750, 15675), (20375, 22750)],
            ENDS=[(False, True), (True, True), (True, False)],
            PIECES0=[(125, 4262), (4262, 18025), (18025, 22625)], LIRA0=[(0, 4262), (4262, 18025), (18025, 22750)], ENDS0=[(False, False)] * 3,
            PLANE=['x', 20050], AXES=[15030, 20030, 29780, 37780],
            CHAIN_X=[-125, 5750, 20375], CHAIN_DIAG=[False, True, True], CHAIN_SIDE='LLL', NOTE_SIDE='RRR', OPEN_R=[True, True, False],
            ZMIN=-4.2, ANALOG_NOTES=False, NOTE_MODE='zone', ONE0=(125, 22625), WH=(42000, 59400), SMOOTH=True, EDGE_GE_MID=True,
            XLO=13500, OPENINGS=[(2, 9175, 14625, 0, 2200)] + [(s, 6675, 7675, 520, 2650) for s in (3, 4, 5, 6)], VLINES=[-125, 13725, 13975, 22875], XLIM=(-100, 22850), CHAIN_OFF_L=[350, 100, 350], CK_SPLIT=6000, OUT='wl/sm11_vert.json')
