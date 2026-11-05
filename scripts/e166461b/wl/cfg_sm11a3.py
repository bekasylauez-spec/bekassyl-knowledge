# См-11 spec (A3 sheet 5.50): hoops as См-7 (same analog): 1-1 two cross-wall ends x 22 levels; 2-2 two cross-wall ends + four free ends
# (three Х2 each) x 92 levels -> Х1 = 228, Х2 = 1332. Concrete: 0.25 x (23.0 x 4.30 + 15.325 x 18.30 - openings 5.45 x 2.2 - 4 x 1.0 x 2.13)
# = 89.71 m3; Шп1 = 89.71 / 0.25 / 0.16 = 2243. Lintels (Bekassyl 06.11): windows 2Ø25 / 2Ø36 per face (rule), large opening 4Ø16 (LIRA).
SPEC = dict(SP='359B50', ST='359DE9', JSONS=['wl/sm11_vert.json', 'wl/sm11_hor.json'], TOTAL_ROW=1, CONC_OFF=2,
            CONC=0.25 * (23.0 * 4.30 + 15.325 * 18.30 - 5.45 * 2.2 - 4 * 1.0 * 2.13), HOOPS=[('Шп1*', 8, 370, 2243), ('Х1*', 8, 930, 228), ('Х2*', 8, 980, 1332)])
