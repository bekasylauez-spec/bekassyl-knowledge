# См-10 spec (A3 sheet 5.44): hoops as in the analog См-7 (4.29) at both ends: free end -> three Х2, end at a cross wall -> Х1 + Х2, ш.200
# levels per zone: basement 22, floors 92, top storey 13. 1-1: 4 cross-wall ends; 2-2: 4 cross-wall + 2 free ends; 3-3: 1 cross-wall + 1 free end
# Х1 = 4*22 + 4*92 + 13 = 469; Х2 = 4*22 + 4*92 + 3*2*92 + 13 + 3*13 = 1060
# concrete: 0.25 x (14.45 x 4.30 + 11.05 x 18.30 + 7.40 x 2.45) = 70.62 m3; Шп1 = 282.48 m2 / 0.16 = 1766
SPEC = dict(SP='303252', ST='3034EB', JSONS=['wl/sm10_vert.json', 'wl/sm10_hor.json'], TOTAL_ROW=1, CONC_OFF=2,
            CONC=0.25 * (14.45 * 4.30 + 11.05 * 18.30 + 7.40 * 2.45), HOOPS=[('Шп1*', 8, 370, 1766), ('Х1*', 8, 930, 469), ('Х2*', 8, 980, 1060)])
