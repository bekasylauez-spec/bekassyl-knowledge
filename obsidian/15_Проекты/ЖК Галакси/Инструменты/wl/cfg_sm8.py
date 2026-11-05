# См-8: axis 2 (x = 6800), analog См-9 (4.33-4.36). Floors -0.100...+19.700: 4 pieces; basement: [-125..7675] (pieces 1+2 merged),
# [15225..18025], [20575..22875]; piece 3 goes on to +21.450 (top storey). Sheet 5.30 (x 2310600), analog axis A = А/1 at 14070.
L = [27614, 32164, 36214, 39364, 42514, 45664, 48814, 51964, 53714]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7, 21.45]
VERT = dict(SX=2310600.0, AX1=14070.0, L=L, LEV=LEV, G=[(0, 1), (1, 3), (3, 5), (5, 7)], PTOP={2: 8},
            PIECES=[(125, 2775), (6175, 7425), (15225, 17775), (20575, 22625)], LIRA=[(0, 2775), (6175, 8000), (15225, 17600), (20875, 22750)],
            ENDS=[(False, True), (True, False), (True, False), (True, False)],
            PIECES0=[(125, 7425), None, (15225, 17775), (20575, 22625)], LIRA0=[(0, 8000), None, (15225, 17600), (20875, 22750)],
            ENDS0=[(False, False), None, (True, False), (True, False)],
            PLANE=['x', 6800], AXES=[14070, 19070, 28820, 36820],
            CHAIN_X=[-125, 6175, 15225, 20575], CHAIN_DIAG=[False, True, True, True], CHAIN_SIDE='LLLL', CHAIN_OFF_L=[350, 350, 650, 350],
            ZMIN=-4.2, ANALOG_NOTES=False, NOTE_MODE='zone', WH=(42000, 59400), XLO=12570,
            VLINES=[-125, 7425, 17775, 22625, 22875], XLIM=(-100, 22850), CK_SPLIT=6000, OUT='wl/sm8_vert.json')
