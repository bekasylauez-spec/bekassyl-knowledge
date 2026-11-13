import io
p=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/rmc_93_baza_shots.cs"
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep('// РМЦ КМ: База Б1 (D-6) тексеру суреттері','// 13.11.2026: A-6 суреттері (қабырға жағынан 3D, ішкі жағынан 3D, план) + A қатарының жалпы 3D-сі; D-6 суреттері бұрынғы нұсқада қалады (файлдар/көріністер өшпейді).\n// РМЦ КМ: База Б1 (D-6) тексеру суреттері (бұрынғы сипаттама)')
rep('const double cx = 30000, cy = 18000,','const double cx = 30000, cy = 266,')
rep('''var names = new[] { "РМЦ_База Б1 D-6 3D юго-запад", "РМЦ_База Б1 D-6 3D северо-восток", "РМЦ_База Б1 D-6 план", "РМЦ_База Б1 D-6 разрез 1-1", "РМЦ_База Б1 D-6 разрез 2-2", "РМЦ_База Б1 D-ряд 3D общий" };
var files = new Dictionary<string, string> { { names[0], "База_Б1_D-6_3D_юго-запад" }, { names[1], "База_Б1_D-6_3D_северо-восток" }, { names[2], "База_Б1_D-6_план" }, { names[3], "База_Б1_D-6_разрез_1-1" }, { names[4], "База_Б1_D-6_разрез_2-2" }, { names[5], "База_Б1_D-ряд_общий" } };
var ids = new Dictionary<string, ElementId>(); var px = new Dictionary<string, int> { { names[0], 2800 }, { names[1], 2800 }, { names[2], 2800 }, { names[3], 2800 }, { names[4], 2800 }, { names[5], 6000 } };''','''var names = new[] { "РМЦ_База Б1 A-6 3D снаружи (со стороны стены)", "РМЦ_База Б1 A-6 3D изнутри", "РМЦ_База Б1 A-6 план", "РМЦ_База Б1 A-ряд 3D общий" };
var files = new Dictionary<string, string> { { names[0], "База_Б1_A-6_3D_снаружи_со_стороны_стены" }, { names[1], "База_Б1_A-6_3D_изнутри" }, { names[2], "База_Б1_A-6_план" }, { names[3], "База_Б1_A-ряд_общий" } };
var ids = new Dictionary<string, ElementId>(); var px = new Dictionary<string, int> { { names[0], 2800 }, { names[1], 2800 }, { names[2], 2800 }, { names[3], 6000 } };''')
rep('new XYZ(1, 1, -0.9), P(cx, cy, 600)','new XYZ(0.6, 1, -0.9), P(cx, cy, 600)')
rep('new XYZ(-1, -1, -0.9), P(cx, cy, 600)','new XYZ(-0.6, -1, -0.9), P(cx, cy, 600)')
rep('ids[names[5]] = mk3(names[5], new XYZ(0.3, 1, -0.6), P(30000, cy, 1000), -1000, cy - 1300, -1100, 61000, cy + 1300, 3500).Id;','ids[names[3]] = mk3(names[3], new XYZ(0.3, 1, -0.6), P(30000, cy, 1000), -1000, cy - 1300, -1100, 61000, cy + 1300, 3500).Id;')
# remove sections
i=s.index('    // section helper:'); j=s.index('    // plan on level')
s=s[:i]+s[j:]
open_=s
rep('"РМЦ_База Б1 D-6 план"','"X"') if False else None
io.open(p,'w',encoding='utf-8',newline='').write(s)
