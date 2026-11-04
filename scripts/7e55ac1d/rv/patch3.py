from PIL import Image
im = Image.open('stamp/whole.png').convert('RGBA')


def save(n, box):
    c = im.crop(box)
    px = c.load()
    for y in range(c.size[1]):
        for x in range(c.size[0]):
            r, g, b, a = px[x, y]
            if r > 190 and g > 190 and b > 190:
                px[x, y] = (255, 255, 255, 0)
    c.save('stamp/%s.png' % n)


save('sig_gip', (447, 271, 592, 316)); save('sig_gap', (447, 321, 592, 373))
save('sig_razr', (447, 378, 592, 428)); save('sig_nk', (447, 488, 592, 538))

k = open('km2.cs', encoding='utf-8').read()


def rep(a, b):
    global k
    assert a in k, a[:80]
    k = k.replace(a, b)


rep('static TextNoteType TextType(Document d, string name, string font, double mm, bool bg)\n        {',
    'static TextNoteType TextType(Document d, string name, string font, double mm, bool bg) { return TextType(d, name, font, mm, bg, 1.0); }\n'
    '        static TextNoteType TextType(Document d, string name, string font, double mm, bool bg, double wf)\n        {')
rep('t.get_Parameter(BuiltInParameter.TEXT_WIDTH_SCALE).Set(1.0);', 't.get_Parameter(BuiltInParameter.TEXT_WIDTH_SCALE).Set(wf);')
rep('TextNoteType g25 = TextType(fd, "КМ_GOST 2,5", GC, 2.5, false), g24 = TextType(fd, "КМ_GOST 2,4", GC, 2.4, false)',
    'TextNoteType g25 = TextType(fd, "КМ_GOST 2,5", GC, 2.5, false, 0.85), g24 = TextType(fd, "КМ_GOST 2,1", GC, 2.1, false, 0.9)')
rep('img("sig_gip.png", 47.5, 28.65, 14.4); img("sig_gap.png", 47.5, 23.8, 14.4); img("sig_razr.png", 47.5, 18.6, 14.4); img("sig_nk.png", 47.5, 8.4, 14.4);',
    'img("sig_gip.png", 48.0, 28.65, 13.4); img("sig_gap.png", 48.0, 23.8, 13.4); img("sig_razr.png", 48.0, 18.6, 13.4); img("sig_nk.png", 48.0, 8.4, 13.4);')
rep('''                // text / dimension styles from the DWG''', '''                Units u = doc.GetUnits();
                u.DecimalSymbol = DecimalSymbol.Comma;
                FormatOptions fl = new FormatOptions(UnitTypeId.Meters); fl.Accuracy = 0.001; fl.UsePlusPrefix = true;
                u.SetFormatOptions(SpecTypeId.Length, fl);
                doc.SetUnits(u);
                // text / dimension styles from the DWG''')
rep('''                foreach (Parameter p in dimT.Parameters) if (p.StorageType == StorageType.Double''', '''                FormatOptions fd2 = new FormatOptions(UnitTypeId.Millimeters); fd2.Accuracy = 1; fd2.UsePlusPrefix = false;
                dimT.SetUnitsFormatOptions(fd2);
                foreach (Parameter p in dimT.Parameters) if (p.StorageType == StorageType.Double''')
rep('"Разрез 1 - 1", new XYZ(4350 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, 9600, 0, 5300', '"Разрез 1 - 1", new XYZ(4350 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1900, 9600, -1300, 5300')
rep('"Разрез 2 - 2", new XYZ(16450 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, 8100, 0, 5300', '"Разрез 2 - 2", new XYZ(16450 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1900, 8100, -1300, 5300')
rep('XYZ.BasisX, -1200, 25200, 0, 5300, 900, 50', 'XYZ.BasisX, -1700, 24700, -1300, 5300, 900, 50')
rep('XYZ.BasisX, -1200, 25200, 0, 5300, 1500, 50', 'XYZ.BasisX, -1700, 24700, -1300, 5300, 1500, 50')
rep('''                    vp.CropBoxActive = true;
                    BoundingBoxXYZ cb = vp.CropBox;
                    cb.Min = new XYZ(-4000 * MM''', '''                    try { vp.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Elev), true); } catch { }
                    vp.CropBoxActive = true;
                    BoundingBoxXYZ cb = vp.CropBox;
                    cb.Min = new XYZ(-4000 * MM''')
rep('''            // marks: tags (fallback''', open('datums.cs.txt', encoding='utf-8').read() + '''
            // marks: tags (fallback''')
rep('''                    HashSet<string> done = new HashSet<string>();
                    foreach (Element e in''', '''                    HashSet<string> done = new HashSet<string>();
                    List<KeyValuePair<string, XYZ>> placed = new List<KeyValuePair<string, XYZ>>();
                    foreach (Element e in''')
rep('''                        try
                        {
                            FamilySymbol ts = col ? tagCol : tagBeam;''', '''                        if (placed.Any(q => q.Key == mk && q.Value.DistanceTo(head) < 900 * MM)) continue;
                        placed.Add(new KeyValuePair<string, XYZ>(mk, head));
                        try
                        {
                            FamilySymbol ts = col ? tagCol : tagBeam;''')
open('km2.cs', 'w', encoding='utf-8').write(k)
print('patched')
