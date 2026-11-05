# См-8 spec (A3 sheet 5.34): hoops Х1/Х2 of the free-end edge zones ш.200 (4 zones x 92 levels floors + 2 x 22 basement + 1 x 8 top = 420);
# concrete: basement 0.25 x 4.30 x 12.9 + floors 0.25 x 18.30 x 9.5 + top 0.25 x 1.50 x 2.8 = 58.38 m3
SPEC = dict(SP='26B1B6', ST='26B44F', JSONS=['wl/sm8_vert.json', 'wl/sm8_hor.json'], TOTAL_ROW=1, CONC_OFF=2,
            CONC=0.25 * 4.30 * 12.9 + 0.25 * 18.30 * 9.5 + 0.25 * 1.50 * 2.8, HOOPS=[('Шп1*', 8, 370, 1460), ('Х1*', 8, 930, 1304), ('Х2*', 8, 980, 464)])
# Шп1 Ø8 L370: S-pins 400x400 staggered, 1 per 0.16 m2 of wall face (05.11)
# 05.11 (Bekassyl: hoops as in the analog at both ends): free end -> two Х1, cross-wall end -> Х1 + Х2 (per level, ш.200)
# 1-1: 4 cross-wall + 2 free ends x 22; 2-2: 4 + 4 x 92; 3-3: 1 + 1 x 8 -> Х1 = 88+88+368+736+8+16 = 1304, Х2 = 88+368+8 = 464
