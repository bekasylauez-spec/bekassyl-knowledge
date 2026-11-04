from PIL import Image
im = Image.open('stamp/whole.png').convert('RGBA')
f = im.size[0] / 2000.0          # the boxes below were read on the 2000 px preview


def save(n, box):
    c = im.crop(tuple(int(round(v * f)) for v in box))
    px = c.load()
    for y in range(c.size[1]):
        for x in range(c.size[0]):
            r, g, b, a = px[x, y]
            if r > 190 and g > 190 and b > 190:
                px[x, y] = (255, 255, 255, 0)
    c.save('stamp/%s.png' % n)
    print(n, c.size)


save('sig_gip', (437, 271, 590, 316)); save('sig_gap', (437, 321, 590, 373))
save('sig_razr', (437, 378, 590, 428)); save('sig_nk', (437, 488, 590, 538))

k = open('km2.cs', encoding='utf-8').read()


def rep(a, b):
    global k
    assert a in k, a[:80]
    k = k.replace(a, b)


rep('TextNoteType g25 = TextType(fd, "КМ_GOST 2,5", GC, 2.5, false, 0.85)', 'TextNoteType g25 = TextType(fd, "КМ_GOST 2,5", GC, 2.5, false, 0.78)')
rep('img("sig_gip.png", 48.0, 28.65, 13.4); img("sig_gap.png", 48.0, 23.8, 13.4); img("sig_razr.png", 48.0, 18.6, 13.4); img("sig_nk.png", 48.0, 8.4, 13.4);',
    'img("sig_gip.png", 47.5, 28.65, 14.2); img("sig_gap.png", 47.5, 23.8, 14.2); img("sig_razr.png", 47.5, 18.6, 14.2); img("sig_nk.png", 47.5, 8.4, 14.2);')
rep('''            string outPath = J["out"];
            SaveAsOptions sao = new SaveAsOptions(); sao.OverwriteExistingFile = true; sao.MaximumBackups = 1;''',
'''            if (J.ContainsKey("pdf"))
            {
                try
                {
                    PDFExportOptions po = new PDFExportOptions();
                    po.Combine = true;
                    po.FileName = Path.GetFileNameWithoutExtension(J["pdf"]);
                    po.PaperFormat = ExportPaperFormat.Default;
                    po.ZoomType = ZoomType.Zoom; po.ZoomPercentage = 100;
                    po.ColorDepth = ColorDepthType.Color;
                    po.RasterQuality = RasterQualityType.High;
                    doc.Export(Path.GetDirectoryName(J["pdf"]), sheets.OrderBy(s => int.Parse(s.SheetNumber)).Select(s => s.Id).ToList(), po);
                    L("pdf " + J["pdf"]);
                }
                catch (Exception ex) { L("pdf " + ex.Message); }
            }
            string outPath = J["out"];
            SaveAsOptions sao = new SaveAsOptions(); sao.OverwriteExistingFile = true; sao.MaximumBackups = 1;''')
open('km2.cs', 'w', encoding='utf-8').write(k)
print('patched')
