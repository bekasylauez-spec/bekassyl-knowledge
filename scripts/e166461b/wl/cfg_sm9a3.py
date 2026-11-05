# См-9 spec (A3 sheet 5.38): hoops Х1 of the two free-end edge zones (left ends of both pieces), 2 per level ш.200 as drawn on 5.37
# (levels per zone: 22 + 19 + 5 x 15 + 13 = 129) -> 2 x 129 x 2 = 516;
# concrete: clear lengths 2.55 + 2.25 = 4.80 m x clear heights 4.30 + 3.80 + 5 x 2.90 + 2.45 = 25.05 m x 0.25 = 30.06 m3
SPEC = dict(SP='29CF8B', ST='29D224', JSONS=['wl/sm9_vert.json', 'wl/sm9_hor.json'], TOTAL_ROW=1, CONC_OFF=2,
            CONC=0.25 * 4.80 * 25.05, HOOPS=[('Шп1*', 8, 370, 752), ('Х1*', 8, 930, 516)])
# Шп1 Ø8 L370: S-pins 400x400 staggered, 1 per 0.16 m2 of wall face (30.06 / 0.25 / 0.16 = 752)
