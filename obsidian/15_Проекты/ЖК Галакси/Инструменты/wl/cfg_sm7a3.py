# См-7 spec (A3 sheet 5.28): hoops of the 4 free-end edge zones (above -0.100) as in См-6: Х1 1 + Х2 2 per level, ш.200 (95 levels per zone);
# concrete: basement 0.25 x 23.0 x 4.30 + piers 0.25 x 17.15 x 18.30 = 103.19 m3
SPEC = dict(SP='217479', ST='217712', JSONS=['wl/sm7_vert.json', 'wl/sm7_hor.json'], TOTAL_ROW=1, CONC_OFF=2, CONC=0.25 * 23.0 * 4.30 + 0.25 * 17.15 * 18.30,
            HOOPS=[('Х1*', 8, 930, 380), ('Х2*', 8, 980, 760)])
