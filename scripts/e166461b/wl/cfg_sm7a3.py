# См-7 spec (A3 sheet 5.28): hoops of the 4 free-end edge zones (above -0.100) as in См-6: Х1 1 + Х2 2 per level, ш.200 (95 levels per zone);
# concrete: basement 0.25 x 23.0 x 4.30 + piers 0.25 x 17.15 x 18.30 = 103.19 m3
SPEC = dict(SP='26A28C', ST='26A525', JSONS=['wl/sm7_vert.json', 'wl/sm7_hor.json'], TOTAL_ROW=1, CONC_OFF=2, CONC=0.25 * 23.0 * 4.30 + 0.25 * 17.15 * 18.30,
            HOOPS=[('Шп1*', 8, 370, 2580), ('Х1*', 8, 930, 228), ('Х2*', 8, 980, 1332)])
# Шп1 Ø8 L370: S-pins 400x400 staggered, 1 per 0.16 m2 of wall face (05.11)
# 05.11 (Bekassyl: hoops as in the analog at both ends): 1-1 two cross-wall ends x 22 levels; 2-2 two cross-wall ends + four free ends
# (three small hoops each) x 92 levels -> Х1 = 2*22 + 2*92 = 228, Х2 = 2*22 + 2*92 + 3*4*92 = 1332
