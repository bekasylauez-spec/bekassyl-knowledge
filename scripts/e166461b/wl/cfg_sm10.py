# См-10: axis 3 (x = 13250), analog См-7 (st2 4.26-4.29). Floors -0.100...+19.700: [-125..2775], [6175..7675], [15225..22875];
# basement: [-125..7675] (pieces 1+2 merged), [15225..22875]; piece 3 goes on to +22.400 (top storey). Sheet 5.41 (x 2733600), А/1 at 13951.
# Ends: P1 left = См-1 corner, P1 right free, P2 left free, P2 right = См-2 band 7425..7675, P3 left = См-4 band 15225..15475, right = См-6.
L = [26341, 30891, 34941, 38091, 41241, 44391, 47541, 50691, 53391]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7, 22.4]
VERT = dict(SX=2733600.0, AX1=13951.0, L=L, LEV=LEV, G=[(0, 1), (1, 3), (3, 5), (5, 7)], PTOP={2: 8},
            PIECES=[(125, 2775), (6175, 7425), (15475, 22625)], LIRA=[(0, 2775), (6175, 8000), (15225, 22750)],
            ENDS=[(False, True), (True, False), (False, False)],
            PIECES0=[(125, 7425), None, (15475, 22625)], LIRA0=[(0, 8000), None, (14750, 22750)], ENDS0=[(False, False), None, (False, False)],
            PLANE=['x', 13250], AXES=[13951, 18951, 28701, 36701],
            CHAIN_X=[-125, 6175, 15225], CHAIN_DIAG=[False, True, True], CHAIN_SIDE='LLL', CHAIN_OFF_L=[350, 350, 650],
            ZMIN=-4.2, ANALOG_NOTES=False, NOTE_MODE='zone', WH=(42000, 59400), XLO=12450, EDGE_GE_MID=True, SMOOTH=True,
            VLINES=[-125, 7425, 15475, 22625, 22875], XLIM=(-100, 22850), CK_SPLIT=6000, OUT='wl/sm10_vert.json')
