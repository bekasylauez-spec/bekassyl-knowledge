# См-8 spec (A3 sheet 5.34): hoops Х1/Х2 of the free-end edge zones ш.200 (4 zones x 92 levels floors + 2 x 22 basement + 1 x 8 top = 420);
# concrete: basement 0.25 x 4.30 x 12.9 + floors 0.25 x 18.30 x 9.5 + top 0.25 x 1.50 x 2.8 = 58.38 m3
SPEC = dict(SP='24CD28', ST='24CFC1', JSONS=['wl/sm8_vert.json', 'wl/sm8_hor.json'], TOTAL_ROW=1, CONC_OFF=2,
            CONC=0.25 * 4.30 * 12.9 + 0.25 * 18.30 * 9.5 + 0.25 * 1.50 * 2.8, HOOPS=[('Х1*', 8, 930, 420), ('Х2*', 8, 980, 840)])
