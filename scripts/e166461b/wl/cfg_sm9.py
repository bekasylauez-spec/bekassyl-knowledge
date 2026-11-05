# См-9: axis x = 10400 (analog См-8 st2, 4.30-4.32). Pieces [15225..17775] (right end at См-5 band 17775..18025), [20375..22625] (См-6 band 22625..22875);
# free ends: left of each piece. Levels -4.650 ... +19.700, +22.400 (top storey 2700). Sheet 5.37 (x 2543100, A2 landscape), axis Б at 9348.
L = [10291, 14841, 18891, 22041, 25191, 28341, 31491, 34641, 37341]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7, 22.4]
VERT = dict(SX=2543100.0, AX1=-5402.0, L=L, LEV=LEV, G=[(0, 1), (1, 3), (3, 5), (5, 8)],
            PIECES=[(15225, 17775), (20375, 22625)], LIRA=[(15225, 17600), (20375, 22750)], ENDS=[(True, False), (True, False)],
            PLANE=['x', 10400], AXES=[9348, 17348],
            CHAIN_X=[15225, 20375], CHAIN_DIAG=[False, True], CHAIN_SIDE='LR', CHAIN_OFF_L=[1500, 350], CHAIN_OFF_R=[350, 700],
            ZMIN=-4.2, ANALOG_NOTES=False, NOTE_MODE='zone', XLO=7800, EDGE_GE_MID=True,
            VLINES=[17775, 18025, 22625, 22875], OUT='wl/sm9_vert.json')
