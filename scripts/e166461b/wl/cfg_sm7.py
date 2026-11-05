# См-7: axis 1 (x = 0); basement -4.650...-0.100 a full wall 125..22625, above three pieces (scheme 2.2-2.4); analog См-6 (4.21-4.25)
L = [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320]
VERT = dict(SX=2036100.0, AX1=15030.0, L=L,
            PIECES=[(125, 3175), (5750, 17100), (20375, 22625)], LIRA=[(0, 3175), (5750, 17100), (20375, 22750)],
            ENDS=[(False, True), (True, True), (True, False)],
            PIECES0=[(125, 4462), (4462, 18737), (18737, 22625)], LIRA0=[(0, 4462), (4462, 18737), (18737, 22750)], ENDS0=[(False, False)] * 3,
            PLANE=['x', 0], AXES=[15030, 20030, 29780, 37780],
            CHAIN_X=[-125, 5750, 20375], CHAIN_DIAG=[False, True, True], CHAIN_SIDE='LLL', NOTE_SIDE='RRR', OPEN_R=[True, True, False],
            ZMIN=-4.2, ANALOG_NOTES=False, NOTE_MODE='zone', ONE0=(125, 22625), WH=(42000, 59400),
            XLO=13500, VLINES=[-125, 13725, 13975, 22875], XLIM=(-100, 22850), CHAIN_OFF_L=[350, 100, 350], CK_SPLIT=6000, OUT='wl/sm7_vert.json')
