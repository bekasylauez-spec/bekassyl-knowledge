p='gen.py'; s=open(p,encoding='utf8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b)
rep("""    for i in range(2, 25):                                 # Р1 at +10.340, bays 3-4 … 25-26
        B('Р1', 'Tb', '□100x5', [AX[i] + 160, y, 10340], [AX[i + 1] - 160, y, 10340])
    for i in (8, 18):""", """    for i in range(0, 27):                                 # Р1 at +10.340 and +5.020 in every bay (ЛИРА 10); row M +5.020 not under the площадка (axes 13–19)
        B('Р1', 'Tb', '□100x5', [AX[i] + 160, y, 10340], [AX[i + 1] - 160, y, 10340])
        if i not in BRACED and not (r == 'M' and 12 <= i <= 17): B('Р1', 'Tb', '□100x5', [AX[i] + 160, y, 5020], [AX[i + 1] - 160, y, 5020])
    for i in BRACED:""")
rep("hs = 50.0\n", "hs = 50.0\nBRACED = (1, 8, 18, 25)                                  # vertical bracing bays 2-3, 9-10, 19-20, 26-27 (ЛИРА)\n")
rep("for r, off in (('A', 750), ('E', -750), ('H', 750), ('M', -750)):\n    y = R[r] + off", "CRANE = (('A', 750), ('E', -750), ('E', 750), ('H', -750), ('H', 750), ('M', -750))   # three crane spans (ЛИРА 8 / 9)\nfor r, off in CRANE:\n    y = R[r] + off")
rep("""for y in (3050.0, 21050.0, 38950.0, 56950.0):
    z = BC(y)
    for i in range(2, 25):""", """P2Y = (3050.0, 9050.0, 15050.0, 21050.0, 38950.0, 44950.0, 50950.0, 56950.0)
for y in P2Y:
    z = BC(y)
    for i in range(1, 26):""")
anchor = "# purlins Пр1 [27П (ЛИРА 18)"
vs = """# ВС1 □100x3 (ЛИРА 6): vertical bracing between the trusses in the braced bays — V from the Р2 strut top (mid-bay) to the top chords at the top nodes
for i in BRACED:
    xm = (AX[i] + AX[i + 1]) / 2
    for yt in (3000.0, 9000.0, 15000.0, 21000.0, 39000.0, 45000.0, 51000.0, 57000.0):
        yb = yt + 50 if yt < 30000 else yt - 50
        for xa in (AX[i], AX[i + 1]):
            a, b = [xm, yb, BC(yb) + 50], [xa, yt, TC(yt)]
            th = math.atan2(b[2] - a[2], abs(xa - xm))
            tb = (BW['20Ш1'] / 2 + 10) / math.cos(th) + 50 * math.tan(th) + 20             # end beside the chord flange tips
            pa, pb = trim(a, b, apex(100, th), tb)
            B('ВС1', 'Tb', '□100x3', pa, pb)
"""
rep(anchor, vs + anchor)
# ГС1 near the ridge (ЛИРА 7, 16 bars missing from sheet 8)
rep("gs = json.load(open(os.path.join(HERE, 'gs1.json')))", """gs = json.load(open(os.path.join(HERE, 'gs1.json')))
gs += [(3000, 27000, 0, 29850), (159000, 27000, 156000, 29850), (51000, 27000, 54000, 29850), (51000, 27000, 48000, 29850), (111000, 27000, 108000, 29850),
       (6000, 30150, 3000, 33000), (162000, 30150, 159000, 33000), (54000, 30150, 51000, 33000), (114000, 30150, 111000, 33000), (0, 30150, 3000, 33000),
       (3000, 27000, 6000, 29850), (159000, 27000, 162000, 29850), (111000, 27000, 114000, 29850), (156000, 30150, 159000, 33000), (108000, 30150, 111000, 33000),
       (48000, 30150, 51000, 33000)]                       # ЛИРА 7 at the ridge (y 29850 / 30150), not on sheet 8""")
# ВФ1 girts on the end walls
anchor2 = "# ---------------- пристройка"
vf = """# ---------------- ВФ1 □100x5 (ЛИРА 10) wall girts on axes 1 / 28 at +6.200 between the columns (К1 rows A/E/H/M: flange face 294.5; СФ: web face 5)
VF_Y = [0, 6000, 12000, 18000, 24000, 27000, 33000, 36000, 42000, 48000, 54000, 60000]
def vf_half(y): return 294.5 + 10 if y in (0, 24000, 36000, 60000) else 5 + 10
for x in (0.0, 162000.0):
    for j in range(len(VF_Y) - 1):
        ya, yb = VF_Y[j], VF_Y[j + 1]
        B('ВФ1', 'Tb', '□100x5', [x, ya + vf_half(ya), 6200], [x, yb - vf_half(yb), 6200])
"""
rep(anchor2, vf + anchor2)
open(p,'w',encoding='utf8').write(s)
