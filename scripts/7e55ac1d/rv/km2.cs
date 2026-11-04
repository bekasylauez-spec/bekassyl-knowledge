using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // КМ album in the style of «КМ Чертеж Навес 1 Рампа.dwg»: RAS stamp «крпкер», ISOCPEUR italic texts, СПДС dims, DWG scales/sheet numbers
    public partial class App
    {
        const string ISO = "ISOCPEUR", GC = "GOST Common";

        static TextNoteType TextType(Document d, string name, string font, double mm, bool bg) { return TextType(d, name, font, mm, bg, 1.0); }
        static TextNoteType TextType(Document d, string name, string font, double mm, bool bg, double wf)
        {
            TextNoteType t = Find<TextNoteType>(d, x => x.Name == name);
            if (t == null)
            {
                TextNoteType b = new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).Cast<TextNoteType>().First();
                t = (TextNoteType)b.Duplicate(name);
            }
            t.get_Parameter(BuiltInParameter.TEXT_FONT).Set(font);
            t.get_Parameter(BuiltInParameter.TEXT_SIZE).Set(mm * MM);
            t.get_Parameter(BuiltInParameter.TEXT_STYLE_ITALIC).Set(1);
            t.get_Parameter(BuiltInParameter.TEXT_STYLE_BOLD).Set(0);
            t.get_Parameter(BuiltInParameter.TEXT_WIDTH_SCALE).Set(wf);
            t.get_Parameter(BuiltInParameter.TEXT_BACKGROUND).Set(bg ? 0 : 1);
            try { t.get_Parameter(BuiltInParameter.TEXT_BOX_VISIBILITY).Set(0); } catch { }
            return t;
        }

        static TextNote Txt(Document d, ElementId viewId, double xmm, double ymm, string s, TextNoteType tt, HorizontalTextAlignment ha, VerticalTextAlignment va, double widthMm)
        {
            TextNoteOptions o = new TextNoteOptions(tt.Id);
            o.HorizontalAlignment = ha;
            o.VerticalAlignment = va;
            TextNote tn = widthMm > 0 ? TextNote.Create(d, viewId, new XYZ(xmm * MM, ymm * MM, 0), widthMm * MM, s, o) : TextNote.Create(d, viewId, new XYZ(xmm * MM, ymm * MM, 0), s, o);
            return tn;
        }

        // titleblock: frame + the «крпкер» stamp (185x55, coordinates taken from the DWG block), logo and signatures as images
        static string MakeTitleblock(Application app, string rft, string dir, string name, double W, double H, string fmt, string stampDir)
        {
            Document fd = app.NewFamilyDocument(rft);
            Tx(fd, "tb", delegate
            {
                View v = new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(x => !x.IsTemplate);
                DelAll(fd, new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds());
                DelAll(fd, new FilteredElementCollector(fd).OfClass(typeof(TextElement)).ToElementIds());
                DelAll(fd, new FilteredElementCollector(fd).OfClass(typeof(TextNote)).ToElementIds());
                // the template keeps its sheet-edge rectangle (locked by size dimensions): move it to the origin and size it W x H
                DelAll(fd, new FilteredElementCollector(fd).OfClass(typeof(Dimension)).ToElementIds());
                foreach (Element ce in new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToList()) { try { ce.Pinned = false; } catch { } }
                DelAll(fd, new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds());
                foreach (ElementId id in new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds().ToList()) { try { fd.Delete(id); } catch (Exception ex) { L("  tb del " + ex.Message); } }
                List<ElementId> rest = new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds().ToList();
                L("  tb " + name + " template lines left: " + rest.Count);
                if (rest.Count > 0)
                {
                    double ox = 1e9, oy = 1e9;
                    foreach (ElementId id in rest) { Curve cv = ((CurveElement)fd.GetElement(id)).GeometryCurve; foreach (int e in new[] { 0, 1 }) { ox = Math.Min(ox, cv.GetEndPoint(e).X); oy = Math.Min(oy, cv.GetEndPoint(e).Y); } }
                    double mx = -1e9, my = -1e9;
                    foreach (ElementId id in rest) { Curve cv = ((CurveElement)fd.GetElement(id)).GeometryCurve; foreach (int e in new[] { 0, 1 }) { mx = Math.Max(mx, cv.GetEndPoint(e).X); my = Math.Max(my, cv.GetEndPoint(e).Y); } }
                    foreach (ElementId id in rest)
                    {
                        CurveElement ce = (CurveElement)fd.GetElement(id);
                        Curve cv = ce.GeometryCurve;
                        XYZ p0 = cv.GetEndPoint(0), p1 = cv.GetEndPoint(1);
                        Func<XYZ, XYZ> map = q => new XYZ(Math.Abs(q.X - ox) < Math.Abs(q.X - mx) ? 0 : W * MM, Math.Abs(q.Y - oy) < Math.Abs(q.Y - my) ? 0 : H * MM, 0);
                        try { ce.SetGeometryCurve(Line.CreateBound(map(p0), map(p1)), true); } catch (Exception ex) { L("  tb edge set " + ex.Message); }
                    }
                    foreach (FamilyParameter fp in fd.FamilyManager.Parameters)
                    {
                        string pn = fp.Definition.Name;
                        if (fp.StorageType != StorageType.Double) continue;
                        if (pn.StartsWith("Ширин") || pn == "Width") fd.FamilyManager.Set(fp, W * MM);
                        if (pn.StartsWith("Высот") || pn == "Height") fd.FamilyManager.Set(fp, H * MM);
                    }
                    foreach (Dimension dm in new FilteredElementCollector(fd).OfClass(typeof(Dimension)).Cast<Dimension>())
                    {
                        if (dm.FamilyLabel == null || !(dm.Curve is Line)) continue;
                        bool vert = Math.Abs(((Line)dm.Curve).Direction.Y) > 0.9;
                        try { fd.FamilyManager.Set(dm.FamilyLabel, (vert ? H : W) * MM); L("  tb size " + dm.FamilyLabel.Definition.Name + " = " + (vert ? H : W)); } catch (Exception ex) { L("  tb size " + ex.Message); }
                    }
                    fd.Regenerate();
                    foreach (ElementId id in rest) { CurveElement ce = (CurveElement)fd.GetElement(id); L("  tb edge " + name + " " + Math.Round(ce.GeometryCurve.GetEndPoint(0).X / MM) + "," + Math.Round(ce.GeometryCurve.GetEndPoint(0).Y / MM) + " -> " + Math.Round(ce.GeometryCurve.GetEndPoint(1).X / MM) + "," + Math.Round(ce.GeometryCurve.GetEndPoint(1).Y / MM)); }
                }
                Category tbc = fd.OwnerFamily.FamilyCategory;
                Category thick = tbc.SubCategories.Contains("КМ_основная") ? tbc.SubCategories.get_Item("КМ_основная") : fd.Settings.Categories.NewSubcategory(tbc, "КМ_основная");
                Category thin = tbc.SubCategories.Contains("КМ_тонкая") ? tbc.SubCategories.get_Item("КМ_тонкая") : fd.Settings.Categories.NewSubcategory(tbc, "КМ_тонкая");
                thick.SetLineWeight(4, GraphicsStyleType.Projection);
                thin.SetLineWeight(1, GraphicsStyleType.Projection);
                thick.LineColor = new Color(0, 0, 0); thin.LineColor = new Color(0, 0, 0);
                Action<double, double, double, double, Category> ln = delegate(double x1, double y1, double x2, double y2, Category c)
                {
                    DetailCurve dc = fd.FamilyCreate.NewDetailCurve(v, Line.CreateBound(new XYZ(x1 * MM, y1 * MM, 0), new XYZ(x2 * MM, y2 * MM, 0)));
                    dc.LineStyle = c.GetGraphicsStyle(GraphicsStyleType.Projection);
                };
                // sheet edge and frame (20 mm binding margin, 5 mm elsewhere)
                ln(0, 0, W, 0, thin); ln(W, 0, W, H, thin); ln(W, H, 0, H, thin); ln(0, H, 0, 0, thin);
                ln(20, 5, W - 5, 5, thick); ln(W - 5, 5, W - 5, H - 5, thick); ln(W - 5, H - 5, 20, H - 5, thick); ln(20, H - 5, 20, 5, thick);
                double sx = W - 5 - 185, sy = 5 - 0.9;
                Action<double, double, double, double, Category> sl = delegate(double x1, double y1, double x2, double y2, Category c) { ln(sx + x1, sy + y1, sx + x2, sy + y2, c); };
                foreach (double y in new[] { 30.9, 45.9, 15.9 }) sl(65, y, 185, y, thick);
                foreach (double y in new[] { 35.9, 30.9 }) sl(0, y, 65, y, thick);
                sl(135, 25.9, 185, 25.9, thick);
                foreach (double x in new[] { 65.0, 40, 20, 55 }) sl(x, 55.9, x, 0.9, thick);
                sl(135, 30.9, 135, 0.9, thick); sl(150, 30.9, 150, 15.9, thick); sl(165, 30.9, 165, 15.9, thick);
                sl(10, 55.9, 10, 30.9, thick); sl(30, 55.9, 30, 30.9, thick);
                foreach (double y in new[] { 40.9, 45.9, 50.9, 5.9, 10.9, 16.1, 21.2, 26.4 }) sl(0, y, 65, y, thin);
                sl(185, 55.9, 0, 55.9, thick); sl(0, 55.9, 0, 0.9, thick);
                // texts
                TextNoteType i25 = TextType(fd, "КМ_ISOCPEUR 2,5", ISO, 2.5, false), i22 = TextType(fd, "КМ_ISOCPEUR 2,2", ISO, 2.2, false);
                TextNoteType g25 = TextType(fd, "КМ_GOST 2,5", GC, 2.5, false, 0.78), g24 = TextType(fd, "КМ_GOST 2,1", GC, 2.1, false, 0.9), g30 = TextType(fd, "КМ_GOST 3,0", GC, 3.0, false);
                Action<double, double, string, TextNoteType, bool, double> tx = delegate(double x, double y, string s, TextNoteType t, bool centre, double w)
                {
                    Txt(fd, v.Id, sx + x, sy + y, s, t, centre ? HorizontalTextAlignment.Center : HorizontalTextAlignment.Left, centre ? VerticalTextAlignment.Middle : VerticalTextAlignment.Top, w);
                };
                tx(142.5, 20.9, "РП", i25, true, 0); tx(142.5, 28.4, "Стадия", i25, true, 0); tx(157.5, 28.4, "Лист", i25, true, 0); tx(175, 28.4, "Листов", i25, true, 0);
                tx(5, 33.4, "Изм.", i22, true, 0); tx(15, 33.4, "Кол.уч.", i22, true, 0); tx(25, 33.4, "Лист", i22, true, 0); tx(35, 33.4, "№док.", i22, true, 0); tx(47.5, 33.4, "Подп.", i22, true, 0); tx(60, 33.4, "Дата", i22, true, 0);
                tx(0.8, 30.2, "ГИП", g25, false, 0); tx(1.0, 25.4, "ГАП", g25, false, 0); tx(0.4, 20.3, "Разработал", g25, false, 0); tx(0.7, 15.2, "Проверил", g25, false, 0); tx(0.6, 10.2, "Н.контроль", g25, false, 0);
                tx(20.6, 30.2, "Казангапов А", g25, false, 0); tx(20.6, 25.4, "Хасанова К", g25, false, 0); tx(20.6, 20.3, "Ауез Б", i25, false, 0); tx(20.6, 10.2, "Приколотов", g25, false, 0);
                foreach (double y in new[] { 30.2, 25.4, 20.3, 15.2, 10.2 }) tx(55.3, y, "06.2026", i22, false, 0);
                tx(125, 50.9, "3669-1-КМ", g30, true, 0);
                tx(125, 38.4, "«Многоквартирный жилой комплекс со встроенными, встроенно-пристроенными помещениями, расположенный по адресу: обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б, 1-я очередь строительства (без наружных инженерных сетей)»", g24, true, 118);
                tx(100, 23.4, "Навес 1 над рампой паркинга", g25, true, 0);
                tx(155, 11.3, "RAS  Group  Project", g25, false, 0); tx(160.8, 7.4, "г. Алматы", g25, false, 0);
                Txt(fd, v.Id, W - 30, 2.2, "Формат " + fmt, g25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                // logo and signatures (cropped from the album PDF)
                Action<string, double, double, double> img = delegate(string file, double cx, double cy, double wmm)
                {
                    string p = Path.Combine(stampDir, file);
                    if (!File.Exists(p)) { L("  no image " + p); return; }
                    ImageType it = ImageType.Create(fd, new ImageTypeOptions(p, false, ImageTypeSource.Import));
                    ImageInstance ii = ImageInstance.Create(fd, v, it.Id, new ImagePlacementOptions(new XYZ((sx + cx) * MM, (sy + cy) * MM, 0), BoxPlacement.Center));
                    ii.Width = wmm * MM;
                };
                img("logo.png", 144.3, 8.3, 15.2);
                img("sig_gip.png", 47.5, 28.65, 14.2); img("sig_gap.png", 47.5, 23.8, 14.2); img("sig_razr.png", 47.5, 18.6, 14.2); img("sig_nk.png", 47.5, 8.4, 14.2);
                FamilyManager fm = fd.FamilyManager;
                if (fm.CurrentType == null) fm.NewType(fmt); else fm.RenameCurrentType(fmt);
            });
            string path = Path.Combine(dir, name + ".rfa");
            SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true;
            fd.SaveAs(path, so); fd.Close(false);
            return path;
        }

        // ISOCPEUR italic in the label types of grid/level/section heads, view titles and tags
        static void RestyleFamilies(Document doc)
        {
            BuiltInCategory[] cats = { BuiltInCategory.OST_GridHeads, BuiltInCategory.OST_LevelHeads, BuiltInCategory.OST_SectionHeads, BuiltInCategory.OST_ViewportLabel,
                BuiltInCategory.OST_StructuralFramingTags, BuiltInCategory.OST_StructuralColumnTags, BuiltInCategory.OST_CalloutHeads };
            foreach (Family f in new FilteredElementCollector(doc).OfClass(typeof(Family)).Cast<Family>().ToList())
            {
                if (!f.IsValidObject || f.FamilyCategory == null || !cats.Any(c => f.FamilyCategory.Id.Value == (long)c) || !f.IsEditable) continue;
                string fname = f.Name;
                try
                {
                    Document fd = doc.EditFamily(f);
                    int n = 0;
                    using (Transaction t = new Transaction(fd, "font"))
                    {
                        t.Start();
                        foreach (ElementType et in new FilteredElementCollector(fd).OfClass(typeof(ElementType)).Cast<ElementType>().Where(x => x is TextElementType))
                        {
                            Parameter p = et.get_Parameter(BuiltInParameter.TEXT_FONT); if (p != null && !p.IsReadOnly) { p.Set(ISO); n++; }
                            Parameter it = et.get_Parameter(BuiltInParameter.TEXT_STYLE_ITALIC); if (it != null && !it.IsReadOnly) it.Set(1);
                        }
                        t.Commit();
                    }
                    if (n > 0) fd.LoadFamily(doc, new LoadOpts());
                    fd.Close(false);
                    L("  font " + fname + " types " + n);
                }
                catch (Exception ex) { L("  font " + fname + " " + ex.Message); }
            }
        }

        static FamilySymbol TagBeamSym, TagColSym;

        static FamilySymbol MarkType(Document doc, FamilySymbol baseSym, string mk)
        {
            FamilySymbol s = baseSym.Family.GetFamilySymbolIds().Select(id => (FamilySymbol)doc.GetElement(id)).FirstOrDefault(x => x.Name == mk);
            if (s == null) s = (FamilySymbol)baseSym.Duplicate(mk);
            if (!s.IsActive) s.Activate();
            return s;
        }

        static string BuildKM2(Application app, Dictionary<string, string> J)
        {
            string famDir = J["famdir"];
            Directory.CreateDirectory(famDir);
            List<string[]> rows = File.ReadAllLines(J["model"], Encoding.UTF8).Where(x => x.Trim().Length > 0).Select(x => x.Split('|')).ToList();
            Dictionary<string, string> beamRfa = new Dictionary<string, string>(), colRfa = new Dictionary<string, string>();
            HashSet<string> colFams = new HashSet<string>(rows.Where(r => r[0] == "C").Select(r => r[1]));
            HashSet<string> beamFams = new HashSet<string>(rows.Where(r => r[0] == "B").Select(r => r[1]));
            foreach (string[] r in rows.Where(r => r[0] == "F"))
            {
                double b = D(r[2]), h = D(r[3]), t = D(r[4]);
                if (beamFams.Contains(r[1])) beamRfa[r[1]] = MakeBeamFamily(app, J["rftbeam"], famDir, r[1], b, h, t);
                if (colFams.Contains(r[1])) colRfa[r[1]] = MakeColumnFamily(app, J["rftcol"], famDir, r[1] + " (стойка)", b, h, t);
            }
            string tbA3 = MakeTitleblock(app, J["rfttb3"], famDir, "КМ_Штамп А3", 420, 297, "А3", J["stampdir"]);
            string tbA2 = MakeTitleblock(app, J["rfttb2"], famDir, "КМ_Штамп А2", 594, 420, "А2", J["stampdir"]);
            string tbA3k = MakeTitleblock(app, J["rfttbn"], famDir, "КМ_Штамп А3 книжный", 297, 420, "А3", J["stampdir"]);
            L("families ok");

            Document doc = app.NewProjectDocument(J["template"]);
            Level lvBase = null, lvTop = null;
            Dictionary<string, FamilySymbol> bs = new Dictionary<string, FamilySymbol>(), csym = new Dictionary<string, FamilySymbol>();
            FamilySymbol tb3 = null, tb2 = null, tb3k = null;
            TextNoteType t30 = null, t25 = null, tTitle = null, t35 = null;
            DimensionType dimT = null;
            Tx(doc, "setup", delegate
            {
                foreach (KeyValuePair<string, string> kv in beamRfa) bs[kv.Key] = LoadSym(doc, kv.Value);
                foreach (KeyValuePair<string, string> kv in colRfa) csym[kv.Key] = LoadSym(doc, kv.Value);
                tb3 = LoadSym(doc, tbA3); tb2 = LoadSym(doc, tbA2); tb3k = LoadSym(doc, tbA3k);
                Material steel = Find<Material>(doc, m => m.Name == "Сталь С245");
                foreach (FamilySymbol s in bs.Values.Concat(csym.Values))
                {
                    Parameter p = s.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM);
                    if (steel != null && p != null && !p.IsReadOnly) p.Set(steel.Id);
                }
                List<Level> lv = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation).ToList();
                lvBase = lv[0]; lvTop = lv[1];
                lvBase.Elevation = 870 * MM; lvBase.Name = "Низ стоек";
                lvTop.Elevation = 4620 * MM; lvTop.Name = "Верх покрытия";
                if (lvBase.GetTypeId() != lvTop.GetTypeId()) lvBase.ChangeTypeId(lvTop.GetTypeId());
                for (int i = 2; i < lv.Count; i++) { try { doc.Delete(lv[i].Id); } catch { } }
                foreach (string[] r in rows.Where(r => r[0] == "G"))
                {
                    Grid g = Grid.Create(doc, Line.CreateBound(new XYZ(D(r[4]) * MM, D(r[5]) * MM, 0), new XYZ(D(r[2]) * MM, D(r[3]) * MM, 0)));
                    g.Name = r[1];
                }
                ProjectInfo pi = doc.ProjectInformation;
                pi.Name = "Навес 1 над рампой паркинга"; pi.Number = "3669-1-КМ";
                pi.Address = "обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б";
                pi.OrganizationName = "ТОО \"RAS Group Project\"";
                Units u = doc.GetUnits();
                u.DecimalSymbol = DecimalSymbol.Comma;
                FormatOptions fl = new FormatOptions(UnitTypeId.Meters); fl.Accuracy = 0.001; fl.UsePlusPrefix = true;
                u.SetFormatOptions(SpecTypeId.Length, fl);
                doc.SetUnits(u);
                // text / dimension styles from the DWG (ISOCPEUR italic; СПДС dims 2.5 with oblique ticks)
                t30 = TextType(doc, "КМ_ISOCPEUR 3,0", ISO, 3.0, false);
                t25 = TextType(doc, "КМ_ISOCPEUR 2,5", ISO, 2.5, false);
                tTitle = TextType(doc, "КМ_Заголовок 3,0", ISO, 3.0, false);
                t35 = TextType(doc, "КМ_ISOCPEUR 3,5", ISO, 3.5, false);
                DimensionType baseLin = new FilteredElementCollector(doc).OfClass(typeof(DimensionType)).Cast<DimensionType>().First(t => t.StyleType == DimensionStyleType.Linear && t.Name.Contains("2,5"));
                DimensionType diag = new FilteredElementCollector(doc).OfClass(typeof(DimensionType)).Cast<DimensionType>().FirstOrDefault(t => t.Name.StartsWith("Диагональ"));
                dimT = Find<DimensionType>(doc, t => t.Name == "КМ_СПДС") ?? (DimensionType)baseLin.Duplicate("КМ_СПДС");
                dimT.get_Parameter(BuiltInParameter.TEXT_FONT).Set(ISO);
                dimT.get_Parameter(BuiltInParameter.TEXT_SIZE).Set(2.5 * MM);
                try { dimT.get_Parameter(BuiltInParameter.TEXT_STYLE_ITALIC).Set(1); } catch { }
                if (diag != null)
                    foreach (Parameter p in diag.Parameters)
                    {
                        if (p.StorageType != StorageType.ElementId) continue;
                        Element ve = doc.GetElement(p.AsElementId());
                        if (ve == null || !ve.Name.Contains("Диагональ")) continue;
                        Parameter q = dimT.LookupParameter(p.Definition.Name);
                        if (q != null && !q.IsReadOnly) { q.Set(p.AsElementId()); L("  dim tick " + p.Definition.Name + " = " + ve.Name); }
                    }
                FormatOptions fd2 = new FormatOptions(UnitTypeId.Millimeters); fd2.Accuracy = 1; fd2.UsePlusPrefix = false;
                dimT.SetUnitsFormatOptions(fd2);
                try { dimT.get_Parameter(BuiltInParameter.WITNS_LINE_EXTENSION).Set(1.25 * MM); } catch (Exception ex) { L("dim ext " + ex.Message); }
                try { dimT.get_Parameter(BuiltInParameter.DIM_LINE_EXTENSION).Set(2.0 * MM); } catch (Exception ex) { L("dim lext " + ex.Message); }
                try { dimT.get_Parameter(BuiltInParameter.TEXT_DIST_TO_LINE).Set(0.8 * MM); } catch (Exception ex) { L("dim off " + ex.Message); }
                foreach (Parameter p in dimT.Parameters)
                    if (p.StorageType == StorageType.Double && p.Definition.Name.StartsWith("Зазор")) { try { p.Set(0.625 * MM); L("  dim " + p.Definition.Name + " = 0,625"); } catch { } }
                foreach (Parameter p in dimT.Parameters) if (p.StorageType == StorageType.Double && p.Definition.Name.Contains("ыносн")) L("  dim param " + p.Definition.Name + " = " + p.AsValueString());
            });
            L("setup ok");
            RestyleFamilies(doc);
            AnnoSet anno = MakeAnnoFamilies(doc, famDir);
            TagBeamSym = anno.TagBeam; TagColSym = anno.TagCol;

            // shared parameters for the spec
            string spf = Path.Combine(JobDir, "km_params.txt");
            if (File.Exists(spf)) File.Delete(spf);
            File.WriteAllText(spf, "", Encoding.Unicode);
            string oldSpf = app.SharedParametersFilename;
            app.SharedParametersFilename = spf;
            Tx(doc, "params", delegate
            {
                DefinitionFile df = app.OpenSharedParameterFile();
                DefinitionGroup grp = df.Groups.Create("КМ");
                CategorySet cs = app.Create.NewCategorySet();
                cs.Insert(Category.GetCategory(doc, BuiltInCategory.OST_StructuralFraming));
                cs.Insert(Category.GetCategory(doc, BuiltInCategory.OST_StructuralColumns));
                cs.Insert(Category.GetCategory(doc, BuiltInCategory.OST_GenericModel));
                foreach (string[] p in new[] { new[] { "КМ_Наименование", "t" }, new[] { "КМ_Сечение", "t" }, new[] { "КМ_Длина_м", "n" }, new[] { "КМ_Масса_кг", "n" }, new[] { "КМ_Масса_1м_кг", "n" }, new[] { "КМ_Порядок", "n" } })
                {
                    Definition def = grp.Definitions.Create(new ExternalDefinitionCreationOptions(p[0], p[1] == "t" ? SpecTypeId.String.Text : SpecTypeId.Number));
                    doc.ParameterBindings.Insert(def, app.Create.NewInstanceBinding(cs), GroupTypeId.Data);
                }
                CategorySet csh = app.Create.NewCategorySet(); csh.Insert(Category.GetCategory(doc, BuiltInCategory.OST_Sheets));
                Definition dsh = grp.Definitions.Create(new ExternalDefinitionCreationOptions("КМ_Порядок_листа", SpecTypeId.Number));
                doc.ParameterBindings.Insert(dsh, app.Create.NewInstanceBinding(csh), GroupTypeId.Data);
            });
            app.SharedParametersFilename = oldSpf;

            // model
            int nb = 0, nc = 0;
            Tx(doc, "frame", delegate
            {
                foreach (string[] r in rows.Where(r => r[0] == "C"))
                {
                    double x = D(r[3]) * MM, y = D(r[4]) * MM, z1 = D(r[5]) * MM, z2 = D(r[6]) * MM;
                    FamilyInstance fi = doc.Create.NewFamilyInstance(new XYZ(x, y, z1), MarkType(doc, csym[r[1]], r[2]), lvBase, StructuralType.Column);
                    fi.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).Set(z1 - lvBase.Elevation);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvTop.Id);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(z2 - lvTop.Elevation);
                    Tag(fi, r[2], r[1], (z2 - z1) / MM / 1000.0, "ЛИРА КЭ " + r[7]);
                    nc++;
                }
                foreach (string[] r in rows.Where(r => r[0] == "B"))
                {
                    XYZ a = new XYZ(D(r[3]) * MM, D(r[4]) * MM, D(r[5]) * MM), b = new XYZ(D(r[6]) * MM, D(r[7]) * MM, D(r[8]) * MM);
                    string mk = r[2];
                    bool brace = mk == "Р1" || mk == "СГ1" || mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "Пк1";
                    FamilyInstance fi = doc.Create.NewFamilyInstance(Line.CreateBound(a, b), MarkType(doc, bs[r[1]], mk), lvBase, brace ? StructuralType.Brace : StructuralType.Beam);
                    StructuralFramingUtils.DisallowJoinAtEnd(fi, 0);
                    StructuralFramingUtils.DisallowJoinAtEnd(fi, 1);
                    Parameter zj = fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION);
                    if (r[9] == "B") { zj.Set((int)ZJustification.Bottom); fi.get_Parameter(BuiltInParameter.Z_OFFSET_VALUE).Set(40 * MM); }
                    else zj.Set((int)ZJustification.Center);
                    Tag(fi, mk, r[1], a.DistanceTo(b) / MM / 1000.0, "ЛИРА КЭ " + r[10]);
                    nb++;
                }
                foreach (string[] r in rows.Where(r => r[0] == "D"))
                {
                    double x = D(r[2]) * MM, y = D(r[3]) * MM, z = D(r[4]) * MM, a = D(r[5]) * MM, b = D(r[6]) * MM, t = D(r[7]) * MM;
                    CurveLoop cl = new CurveLoop();
                    XYZ p1 = new XYZ(x - a / 2, y - b / 2, z - t), p2 = new XYZ(x + a / 2, y - b / 2, z - t), p3 = new XYZ(x + a / 2, y + b / 2, z - t), p4 = new XYZ(x - a / 2, y + b / 2, z - t);
                    cl.Append(Line.CreateBound(p1, p2)); cl.Append(Line.CreateBound(p2, p3)); cl.Append(Line.CreateBound(p3, p4)); cl.Append(Line.CreateBound(p4, p1));
                    DirectShape ds = DirectShape.CreateElement(doc, new ElementId(BuiltInCategory.OST_GenericModel));
                    ds.SetShape(new List<GeometryObject> { GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { cl }, XYZ.BasisZ, t) });
                    try { ds.SetName(r[1]); } catch { }
                    SetP(ds, BuiltInParameter.ALL_MODEL_MARK, r[1]);
                    SetP(ds, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, "Закладная деталь (раздел КЖ)");
                }
            });
            L("columns " + nc + " framing " + nb);
            Tx(doc, "plates", delegate { AddPlates(doc, lvBase, lvTop); });

            Dictionary<string, ElementId> flt = new Dictionary<string, ElementId>();
            ElementId solid = new FilteredElementCollector(doc).OfClass(typeof(FillPatternElement)).Cast<FillPatternElement>().First(f => f.GetFillPattern().IsSolidFill).Id;
            Tx(doc, "filters", delegate
            {
                List<ElementId> cats = new List<ElementId> { new ElementId(BuiltInCategory.OST_StructuralFraming), new ElementId(BuiltInCategory.OST_StructuralColumns), new ElementId(BuiltInCategory.OST_GenericModel) };
                foreach (string mk in Marks)
                    flt[mk] = ParameterFilterElement.Create(doc, "КМ_" + mk, cats, new ElementParameterFilter(ParameterFilterRuleFactory.CreateEqualsRule(new ElementId(BuiltInParameter.ALL_MODEL_MARK), mk))).Id;
            });

            // views (scales as on the DWG sheets: plans 1:75, sections 1:50)
            ViewFamilyType vtPlan = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.StructuralPlan);
            ViewFamilyType vtSec = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section && v.Name == "Разрез") ?? Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section);
            ViewFamilyType vt3d = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.ThreeDimensional);
            ApplyAnno(doc, anno, vtSec, Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Detail), vtPlan);
            Dictionary<string, View> V = new Dictionary<string, View>();
            string[][] plans = {
                new[]{ "p3", "Схема расположения закладных деталей", "К1,К2,Зд-1,Зд-2" },
                new[]{ "p4", "Схема расположения стоек и вертикальных связей", "К1,К2,СВ1,СВ2" },
                new[]{ "p5", "Схема расположения ферм и связей покрытия по нижним поясам ферм навеса", "НП1,СГ1,РС1,СВ3" },
                new[]{ "p6", "Схема расположения ферм и прогонов покрытия по верхним поясам ферм навеса", "ВП1,П1" } };
            Tx(doc, "views", delegate
            {
                foreach (string[] pl in plans)
                {
                    ViewPlan vp = ViewPlan.Create(doc, vtPlan.Id, lvBase.Id);
                    vp.Name = pl[1];
                    vp.Scale = 75;
                    PlanViewRange pr = vp.GetViewRange();
                    pr.SetLevelId(PlanViewPlane.TopClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.TopClipPlane, 5000 * MM);
                    pr.SetLevelId(PlanViewPlane.CutPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.CutPlane, 4900 * MM);
                    pr.SetLevelId(PlanViewPlane.BottomClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.BottomClipPlane, -100 * MM);
                    pr.SetLevelId(PlanViewPlane.ViewDepthPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.ViewDepthPlane, -100 * MM);
                    vp.SetViewRange(pr);
                    vp.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(pl[1]);
                    vp.DisplayStyle = DisplayStyle.HLR;
                    StyleView(doc, vp, flt, solid, pl[2].Split(','));
                    if (pl[0] != "p3") { try { vp.SetCategoryHidden(new ElementId(BuiltInCategory.OST_GenericModel), true); } catch { } }
                    try { vp.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Elev), true); } catch { }
                    vp.CropBoxActive = true;
                    BoundingBoxXYZ cb = vp.CropBox;
                    cb.Min = new XYZ(-4000 * MM, -4000 * MM, cb.Min.Z); cb.Max = new XYZ(25300 * MM, 11300 * MM, cb.Max.Z);
                    vp.CropBox = cb; vp.CropBoxVisible = false;
                    V[pl[0]] = vp;
                }
                V["1-1"] = Sec(doc, vtSec.Id, "1", "Разрез 1 - 1", new XYZ(4350 * MM - 150 * MM, 0, 0), XYZ.BasisY, -2900, 9600, -1300, 5300, 1200, 50);
                V["2-2"] = Sec(doc, vtSec.Id, "2", "Разрез 2 - 2", new XYZ(16450 * MM - 150 * MM, 0, 0), XYZ.BasisY, -2900, 8100, -1300, 5300, 1200, 50);
                V["3-3"] = Sec(doc, vtSec.Id, "3", "Разрез 3 - 3", new XYZ(0, 7700 * MM, 0), XYZ.BasisX, -1700, 24700, -1300, 5300, 900, 50);
                V["4-4"] = Sec(doc, vtSec.Id, "4", "Разрез 4 - 4", new XYZ(0, 400 * MM, 0), XYZ.BasisX, -1700, 24700, -1300, 5300, 1500, 50);
                foreach (string k in new[] { "1-1", "2-2", "3-3", "4-4" })
                {
                    V[k].DisplayStyle = DisplayStyle.HLR;
                    StyleView(doc, V[k], flt, solid, null);
                    try { V[k].SetCategoryHidden(new ElementId(BuiltInCategory.OST_Sections), true); } catch { }
                    V[k].CropBoxVisible = false;
                }
                foreach (string[] fs in new[] { new[] { "Ф1", "4350", "9600" }, new[] { "Ф2", "16450", "8100" } })
                {
                    ViewSection sv = Sec(doc, vtSec.Id, "Схема " + fs[0], "Геометрическая схема фермы " + fs[0], new XYZ(D(fs[1]) * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, D(fs[2]), 1500, 5300, 400, 50);
                    sv.DetailLevel = ViewDetailLevel.Coarse;
                    sv.DisplayStyle = DisplayStyle.HLR;
                    StyleView(doc, sv, flt, solid, new[] { "ВП1", "НП1", "Р1" });
                    sv.DetailLevel = ViewDetailLevel.Coarse;
                    try { sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), true); sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Sections), true); sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_GenericModel), true); } catch { }
                    try { sv.get_Parameter(BuiltInParameter.SECTION_COARSER_SCALE_PULLDOWN_METRIC).Set(20); } catch (Exception ex) { L("hide marker " + ex.Message); }
                    sv.CropBoxVisible = false;
                    V["s" + fs[0]] = sv;
                }
                View3D v3 = View3D.CreateIsometric(doc, vt3d.Id);
                v3.Name = "Общий вид каркаса навеса";
                XYZ f0 = new XYZ(1, 1, -0.7).Normalize();
                v3.SetOrientation(new ViewOrientation3D(new XYZ(-40, -30, 25), f0.CrossProduct(XYZ.BasisZ).CrossProduct(f0).Normalize(), f0));
                v3.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set("Общий вид каркаса навеса");
                StyleView(doc, v3, flt, solid, null);
                v3.DisplayStyle = DisplayStyle.ShadingWithEdges;
                v3.Scale = 100;
                try { v3.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Grids), true); v3.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), true); } catch { }
                V["3d"] = v3;
            });
            L("views ok");
            ViewFamilyType vtDet = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Detail);
            Dictionary<string, View> NV = new Dictionary<string, View>();
            Tx(doc, "nodes", delegate
            {
                // node marks with the circle (DWG): callout tag «M_Заголовок фрагмента» for detail and plan callouts
                ElementType ct = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>()
                    .FirstOrDefault(t => t.FamilyName == "Марка фрагмента" && t.LookupParameter("Заголовок фрагмента") != null && doc.GetElement(t.LookupParameter("Заголовок фрагмента").AsElementId()) != null && doc.GetElement(t.LookupParameter("Заголовок фрагмента").AsElementId()).Name.StartsWith("M_"));
                L("callout tag " + (ct != null ? ct.Name : "-"));
                if (ct != null && anno.Callout == null)
                    foreach (ViewFamilyType vft in new[] { vtDet, vtPlan, vtSec })
                    {
                        Parameter pc = vft.LookupParameter("Марка фрагмента");
                        if (pc != null && !pc.IsReadOnly) pc.Set(ct.Id); else L("no callout tag param on " + vft.Name);
                    }
                NV = NodeViews(doc, V, vtDet.Id, vtPlan.Id, lvBase);
                foreach (string nk in new[] { "8", "9" })
                {
                    if (!NV.ContainsKey(nk) || !(NV[nk] is ViewPlan)) continue;
                    ViewPlan np = (ViewPlan)NV[nk];
                    PlanViewRange pr = np.GetViewRange();
                    pr.SetLevelId(PlanViewPlane.BottomClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.BottomClipPlane, (nk == "8" ? 1250 : 2550) * MM);
                    pr.SetLevelId(PlanViewPlane.ViewDepthPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.ViewDepthPlane, (nk == "8" ? 1250 : 2550) * MM);
                    np.SetViewRange(pr);
                }
                foreach (KeyValuePair<string, View> kv in NV)
                {
                    View nv = kv.Value;
                    StyleView(doc, nv, flt, solid, (kv.Key == "8" || kv.Key == "9") ? new[] { "НП1", "СГ1", "РС1", "СВ3" } : null);
                    foreach (ElementId fid in nv.GetFilters())
                    {
                        OverrideGraphicSettings o = nv.GetFilterOverrides(fid);
                        OverrideGraphicSettings o2 = new OverrideGraphicSettings();
                        o2.SetProjectionLineColor(o.ProjectionLineColor); o2.SetCutLineColor(o.CutLineColor);
                        o2.SetProjectionLineWeight(4); o2.SetCutLineWeight(5);
                        nv.SetFilterOverrides(fid, o2);
                    }
                    try { nv.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(1); } catch (Exception ex) { L("acrop " + ex.Message); }
                    try
                    {
                        ViewCropRegionShapeManager sm = nv.GetCropRegionShapeManager();
                        double off = 22 * MM;
                        sm.TopAnnotationCropOffset = off; sm.BottomAnnotationCropOffset = off; sm.LeftAnnotationCropOffset = off; sm.RightAnnotationCropOffset = off;
                    }
                    catch (Exception ex) { L("acrop off " + ex.Message); }
                    foreach (BuiltInCategory hc in new[] { BuiltInCategory.OST_Grids, BuiltInCategory.OST_Levels, BuiltInCategory.OST_Sections, BuiltInCategory.OST_Elev, BuiltInCategory.OST_Callouts, BuiltInCategory.OST_ReferenceViewer })
                    { try { nv.SetCategoryHidden(new ElementId(hc), true); } catch { } }
                }
            });
            L("nodes " + NV.Count);

            // dimensions (grid chains, frame spacing) in the plans
            Tx(doc, "dims", delegate
            {
                List<Grid> grids = new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>().ToList();
                List<Grid> gx = grids.Where(g => Math.Abs(((Line)g.Curve).Direction.Y) > 0.9).OrderBy(g => g.Curve.GetEndPoint(0).X).ToList();
                List<Grid> gy = grids.Where(g => Math.Abs(((Line)g.Curve).Direction.X) > 0.9).OrderBy(g => g.Curve.GetEndPoint(0).Y).ToList();
                List<FamilyInstance> colsL = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>()
                    .Where(c => Math.Abs(((LocationPoint)c.Location).Point.Y) < 0.01).OrderBy(c => ((LocationPoint)c.Location).Point.X).ToList();
                foreach (string k in new[] { "p3", "p4", "p5", "p6" })
                {
                    View v = V[k];
                    try
                    {
                        ReferenceArray rc = new ReferenceArray();
                        foreach (FamilyInstance c in colsL) rc.Append(c.GetReferences(FamilyInstanceReferenceType.CenterLeftRight).First());
                        ReferenceArray ra = new ReferenceArray(); foreach (Grid g in gx) ra.Append(new Reference(g));
                        ra.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1300 * MM, 0), new XYZ(1, -1300 * MM, 0)), ra, dimT);
                        ReferenceArray ro = new ReferenceArray(); ro.Append(new Reference(gx.First())); ro.Append(new Reference(gx.Last()));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1900 * MM, 0), new XYZ(1, -1900 * MM, 0)), ro, dimT);
                        ReferenceArray rl = new ReferenceArray(); foreach (Grid g in gy) rl.Append(new Reference(g));
                        string rowMk = k == "p5" ? "РС1" : k == "p6" ? "П1" : null;
                        List<FamilyInstance> rowEls = rowMk == null ? new List<FamilyInstance>() : new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
                            .Where(f => f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == rowMk && ((LocationCurve)f.Location).Curve.GetEndPoint(0).X > 21000 * MM).GroupBy(f => Math.Round(((LocationCurve)f.Location).Curve.GetEndPoint(0).Y / MM)).Select(g => g.First()).OrderBy(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y).ToList();
                        FamilyInstance cant = rowEls.FirstOrDefault(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y < -600 * MM);
                        if (cant != null) { Reference cr = cant.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (cr != null) rl.Append(cr); }
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(-1900 * MM, 0, 0), new XYZ(-1900 * MM, 1, 0)), rl, dimT);
                        if (rowEls.Count > 1)
                        {
                            ReferenceArray rr = new ReferenceArray();
                            foreach (FamilyInstance f in rowEls) { Reference r0 = f.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (r0 != null) rr.Append(r0); }
                            if (rr.Size > 1) doc.Create.NewDimension(v, Line.CreateBound(new XYZ(24700 * MM, 0, 0), new XYZ(24700 * MM, 1, 0)), rr, dimT);
                        }
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, 10000 * MM, 0), new XYZ(1, 10000 * MM, 0)), rc, dimT);
                        ReferenceArray rco = new ReferenceArray(); rco.Append(rc.get_Item(0)); rco.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, 10600 * MM, 0), new XYZ(1, 10600 * MM, 0)), rco, dimT);
                    }
                    catch (Exception ex) { L("dims " + k + " " + ex.Message); }
                }
            });

            Tx(doc, "datums", delegate
            {
                List<Grid> grids = new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>().ToList();
                foreach (string k in new[] { "p3", "p4", "p5", "p6" })
                    foreach (Grid g in grids)
                    {
                        try
                        {
                            Curve c = g.GetCurvesInView(DatumExtentType.Model, V[k])[0];
                            XYZ a0 = c.GetEndPoint(0), a1 = c.GetEndPoint(1);
                            bool vert = Math.Abs(a0.X - a1.X) < Math.Abs(a0.Y - a1.Y);
                            bool lowIs0 = vert ? a0.Y < a1.Y : a0.X < a1.X;
                            g.HideBubbleInView(DatumEnds.End0, V[k]); g.HideBubbleInView(DatumEnds.End1, V[k]);
                            g.ShowBubbleInView(lowIs0 ? DatumEnds.End0 : DatumEnds.End1, V[k]);
                            if (k == "p3" && g.Name == "1") L("  bubble grid 1: end0 " + Math.Round(a0.Y / MM) + " end1 " + Math.Round(a1.Y / MM) + " show " + (lowIs0 ? "End0" : "End1") + " vis0 " + g.IsBubbleVisibleInView(DatumEnds.End0, V[k]) + " vis1 " + g.IsBubbleVisibleInView(DatumEnds.End1, V[k]));
                        }
                        catch (Exception ex) { L("bubble " + ex.Message); }
                    }
                List<Level> levels = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().ToList();
                foreach (Level lv in levels)
                {
                    try
                    {
                        Curve c3 = lv.GetCurvesInView(DatumExtentType.Model, V["3-3"])[0];
                        double yy = c3.GetEndPoint(0).Y;
                        lv.SetCurveInView(DatumExtentType.Model, V["3-3"], Line.CreateBound(new XYZ(-4000 * MM, yy, lv.Elevation), new XYZ(28000 * MM, yy, lv.Elevation)));
                        Curve c1 = lv.GetCurvesInView(DatumExtentType.Model, V["1-1"])[0];
                        double xx = c1.GetEndPoint(0).X;
                        lv.SetCurveInView(DatumExtentType.Model, V["1-1"], Line.CreateBound(new XYZ(xx, -4000 * MM, lv.Elevation), new XYZ(xx, 12000 * MM, lv.Elevation)));
                    }
                    catch (Exception ex) { L("level model ext " + ex.Message); }
                }
                foreach (string k in new[] { "1-1", "2-2", "3-3", "4-4" })
                {
                    View v = V[k];
                    BoundingBoxXYZ cb = v.CropBox;
                    XYZ left = cb.Transform.OfPoint(new XYZ(cb.Min.X, 0, 0)), right = cb.Transform.OfPoint(new XYZ(cb.Max.X, 0, 0));
                    if ((right - left).DotProduct(v.RightDirection) < 0) { XYZ tmp = left; left = right; right = tmp; }
                    XYZ rd = (right - left).Normalize();
                    foreach (Level lv in levels)
                    {
                        try
                        {
                            lv.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific);
                            lv.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific);
                            XYZ pa = new XYZ(left.X, left.Y, lv.Elevation) + rd * (250 * MM), pb = pa + rd * (20 * MM * v.Scale);
                            lv.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(pa, pb));
                            lv.ShowBubbleInView(DatumEnds.End0, v); lv.HideBubbleInView(DatumEnds.End1, v);
                        }
                        catch (Exception ex) { L("level ends " + k + " " + ex.Message); }
                    }
                    foreach (Grid g in grids)
                    {
                        try
                        {
                            IList<Curve> cs = g.GetCurvesInView(DatumExtentType.ViewSpecific, v);
                            if (cs.Count == 0) continue;
                            XYZ p = cs[0].GetEndPoint(0);
                            g.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific);
                            g.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific);
                            g.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(new XYZ(p.X, p.Y, -900 * MM), new XYZ(p.X, p.Y, 5000 * MM)));
                            g.ShowBubbleInView(DatumEnds.End0, v); g.HideBubbleInView(DatumEnds.End1, v);
                        }
                        catch (Exception ex) { L("grid ends " + k + " " + ex.Message); }
                    }
                }
                // section dimensions: rows Л-М and the К2 row; grid chain and column spacing along the rows
                Grid gL = grids.First(g => g.Name == "Л"), gM = grids.First(g => g.Name == "М");
                List<FamilyInstance> cols = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
                Func<FamilyInstance, XYZ> P = c => ((LocationPoint)c.Location).Point;
                foreach (string[] s in new[] { new[] { "1-1", "4350" }, new[] { "2-2", "16450" } })
                {
                    try
                    {
                        double x = D(s[1]) * MM;
                        ReferenceArray ra = new ReferenceArray(); ra.Append(new Reference(gL)); ra.Append(new Reference(gM));
                        FamilyInstance k2 = cols.FirstOrDefault(c => Math.Abs(P(c).X - x) < 0.01 && P(c).Y > 8000 * MM);
                        if (k2 != null) ra.Append(k2.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).First());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, 0, 300 * MM), new XYZ(x, 1, 300 * MM)), ra, dimT);
                        ReferenceArray rp = new ReferenceArray();
                        foreach (FamilyInstance f in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
                            .Where(f => f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == "П1").Where(f => { Curve cv = ((LocationCurve)f.Location).Curve; double a0 = Math.Min(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X), a1 = Math.Max(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X); return a0 < x + 300 * MM && a1 > x + 300 * MM; })
                            .OrderBy(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y))
                        { Reference r0 = f.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (r0 != null) rp.Append(r0); }
                        if (rp.Size > 1) doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, 0, 5000 * MM), new XYZ(x, 1, 5000 * MM)), rp, dimT);
                        ReferenceArray rlv = new ReferenceArray(); foreach (Level lv in levels) rlv.Append(lv.GetPlaneReference());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, -1500 * MM, 0), new XYZ(x, -1500 * MM, 1)), rlv, dimT);
                    }
                    catch (Exception ex) { L("sec dims " + s[0] + " " + ex.Message); }
                }
                List<Grid> gx = grids.Where(g => Math.Abs(((Line)g.Curve).Direction.Y) > 0.9).OrderBy(g => Math.Min(g.Curve.GetEndPoint(0).X, g.Curve.GetEndPoint(1).X)).ToList();
                foreach (string[] s in new[] { new[] { "3-3", "7300" }, new[] { "4-4", "0" } })
                {
                    try
                    {
                        double y = D(s[1]) * MM;
                        ReferenceArray rg = new ReferenceArray(); foreach (Grid g in gx) rg.Append(new Reference(g));
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, -300 * MM), new XYZ(1, y, -300 * MM)), rg, dimT);
                        ReferenceArray rc = new ReferenceArray();
                        foreach (FamilyInstance c in cols.Where(c => Math.Abs(P(c).Y - y) < 0.01).OrderBy(c => P(c).X)) rc.Append(c.GetReferences(FamilyInstanceReferenceType.CenterLeftRight).First());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, 300 * MM), new XYZ(1, y, 300 * MM)), rc, dimT);
                        ReferenceArray rco = new ReferenceArray(); rco.Append(rc.get_Item(0)); rco.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, -900 * MM), new XYZ(1, y, -900 * MM)), rco, dimT);
                        ReferenceArray rlv = new ReferenceArray(); foreach (Level lv in levels) rlv.Append(lv.GetPlaneReference());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(-1200 * MM, y, 0), new XYZ(-1200 * MM, y, 1)), rlv, dimT);
                    }
                    catch (Exception ex) { L("sec dims " + s[0] + " " + ex.Message); }
                }
            });

            // marks: tags (fallback to text with the mark if the tag family shows something else)
            Tx(doc, "tags", delegate
            {
                FamilySymbol tagBeam = TagBeamSym, tagCol = TagColSym;
                if (tagBeam != null && !tagBeam.IsActive) tagBeam.Activate();
                if (tagCol != null && !tagCol.IsActive) tagCol.Activate();
                L("tags: " + (tagBeam != null ? tagBeam.FamilyName + ":" + tagBeam.Name : "-") + " / " + (tagCol != null ? tagCol.FamilyName + ":" + tagCol.Name : "-"));
                Dictionary<string, string[]> each = new Dictionary<string, string[]> {
                    { "p3", new string[0] }, { "p4", new[] { "К1", "К2" } }, { "p5", new[] { "РС1", "СГ1", "СВ3" } }, { "p6", new[] { "П1" } } };
                int bad = 0;
                foreach (string k in each.Keys)
                {
                    View v = V[k];
                    HashSet<string> done = new HashSet<string>();
                    List<KeyValuePair<string, XYZ>> placed = new List<KeyValuePair<string, XYZ>>();
                    foreach (Element e in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().Where(e => e.Category != null && (e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList())
                    {
                        string mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString();
                        if (mk == null || !Visible(v, flt, mk)) continue;
                        if (!each[k].Contains(mk) && done.Contains(mk)) continue;
                        bool col = e.Location is LocationPoint;
                        XYZ p, head;
                        if (col) { p = ((LocationPoint)e.Location).Point; head = new XYZ(p.X + 400 * MM, p.Y + 450 * MM, 0); }
                        else
                        {
                            Curve c = ((LocationCurve)e.Location).Curve; p = c.Evaluate(0.5, true);
                            XYZ dir = (c.GetEndPoint(1) - c.GetEndPoint(0)); dir = new XYZ(dir.X, dir.Y, 0);
                            bool alongX = dir.GetLength() > 1e-6 && Math.Abs(dir.Normalize().X) > 0.95;
                            head = alongX ? new XYZ(p.X, p.Y + 230 * MM, 0) : new XYZ(p.X + 300 * MM, p.Y + 300 * MM, 0);
                        }
                        if (placed.Any(q => q.Key == mk && q.Value.DistanceTo(head) < 1600 * MM)) continue;
                        for (int g = 0; g < 4 && placed.Any(q => q.Key != mk && q.Value.DistanceTo(head) < 600 * MM); g++) head = head + new XYZ(0, 550 * MM, 0);
                        placed.Add(new KeyValuePair<string, XYZ>(mk, head));
                        try
                        {
                            FamilySymbol ts = col ? tagCol : tagBeam;
                            bool ok = false;
                            if (ts != null)
                            {
                                IndependentTag tg = IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), true, TagOrientation.Horizontal, head);
                                if (tg.TagText == mk) ok = true; else { if (bad++ < 3) L("  tag shows '" + tg.TagText + "' for " + mk); doc.Delete(tg.Id); }
                            }
                            if (!ok)
                            {
                                TextNote tn = Txt(doc, v.Id, head.X / MM, head.Y / MM, mk, t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                                FormattedText uf = tn.GetFormattedText(); uf.SetUnderlineStatus(true); tn.SetFormattedText(uf);
                                if (col) { Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = new XYZ(p.X, p.Y, 0); }
                            }
                            done.Add(mk);
                        }
                        catch (Exception ex) { L("tag " + mk + " " + ex.Message); }
                    }
                }
                // embedded parts: one callout each
                foreach (string zd in new[] { "Зд-1", "Зд-2" })
                {
                    Element e = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().FirstOrDefault(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == zd);
                    if (e == null) continue;
                    BoundingBoxXYZ bb = e.get_BoundingBox(null);
                    XYZ c = (bb.Min + bb.Max) / 2;
                    TextNote tn = Txt(doc, V["p3"].Id, c.X / MM + 500, c.Y / MM + 700, zd, t30, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                    Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = new XYZ(c.X, c.Y, 0);
                }
            });
            Tx(doc, "node marks", delegate { foreach (View nv in NV.Values) NodeMarks(doc, nv, t25); });
            L("tags ok");

            FamilySymbol[] signs = MakeSectionSigns(app, doc, J["rftanno"], famDir);
            Tx(doc, "section signs", delegate { SectionSigns(doc, V, signs, t30); });
            // spec
            ViewSchedule spec = null;
            Tx(doc, "spec", delegate
            {
                spec = ViewSchedule.CreateSchedule(doc, ElementId.InvalidElementId);
                spec.Name = "Ведомость элементов";
                ScheduleDefinition sd = spec.Definition;
                Dictionary<string, SchedulableField> sf = new Dictionary<string, SchedulableField>();
                foreach (SchedulableField f in sd.GetSchedulableFields()) { string n = f.GetName(doc); if (!sf.ContainsKey(n)) sf[n] = f; }
                ScheduleField fMark = sd.AddField(sf.ContainsKey("Марка") ? sf["Марка"] : new SchedulableField(ScheduleFieldType.Instance, new ElementId(BuiltInParameter.ALL_MODEL_MARK)));
                ScheduleField fName = sd.AddField(sf["КМ_Наименование"]);
                ScheduleField fSec = sd.AddField(sf["КМ_Сечение"]);
                ScheduleField fCnt = sd.AddField(ScheduleFieldType.Count);
                ScheduleField fLen = sd.AddField(sf["КМ_Длина_м"]);
                ScheduleField fKgm = sd.AddField(sf["КМ_Масса_1м_кг"]);
                ScheduleField fMass = sd.AddField(sf["КМ_Масса_кг"]);
                ScheduleField fOrd = sd.AddField(sf["КМ_Порядок"]); fOrd.IsHidden = true;
                fMark.ColumnHeading = "Марка"; fName.ColumnHeading = "Наименование"; fSec.ColumnHeading = "Сечение, ГОСТ 30245-2012"; fCnt.ColumnHeading = "Кол-во, шт";
                fLen.ColumnHeading = "Длина общая, м"; fKgm.ColumnHeading = "Масса 1 м, кг"; fMass.ColumnHeading = "Масса общая, кг";
                fLen.DisplayType = ScheduleFieldDisplayType.Totals; fMass.DisplayType = ScheduleFieldDisplayType.Totals;
                sd.AddFilter(new ScheduleFilter(fMass.FieldId, ScheduleFilterType.GreaterThan, 0.0));
                sd.AddSortGroupField(new ScheduleSortGroupField(fOrd.FieldId));
                sd.AddSortGroupField(new ScheduleSortGroupField(fMark.FieldId));
                double[] wmm = { 15, 58, 30, 15, 22, 18, 24 };
                ScheduleField[] ff = { fMark, fName, fSec, fCnt, fLen, fKgm, fMass };
                for (int i = 0; i < ff.Length; i++) ff[i].GridColumnWidth = wmm[i] * MM;
                sd.IsItemized = false;
                sd.ShowGrandTotal = true; sd.ShowGrandTotalTitle = true; sd.GrandTotalTitle = "Итого";
                try { spec.BodyTextTypeId = t25.Id; spec.HeaderTextTypeId = t25.Id; spec.TitleTextTypeId = t30.Id; } catch (Exception ex) { L("spec text " + ex.Message); }
            });

            // sheet list for «Общие данные»
            ViewSchedule sheetList = null;
            Tx(doc, "sheet list", delegate
            {
                sheetList = ViewSchedule.CreateSheetList(doc);
                sheetList.Name = "Ведомость рабочих чертежей основного комплекта";
                ScheduleDefinition sd = sheetList.Definition;
                Dictionary<string, SchedulableField> sf = new Dictionary<string, SchedulableField>();
                foreach (SchedulableField f in sd.GetSchedulableFields()) { string n = f.GetName(doc); if (!sf.ContainsKey(n)) sf[n] = f; }
                ScheduleField fn = sd.AddField(new SchedulableField(ScheduleFieldType.Instance, new ElementId(BuiltInParameter.SHEET_NUMBER)));
                ScheduleField fm = sd.AddField(new SchedulableField(ScheduleFieldType.Instance, new ElementId(BuiltInParameter.SHEET_NAME)));
                ScheduleField fo = sd.AddField(sf["КМ_Порядок_листа"]); fo.IsHidden = true;
                fn.ColumnHeading = "Лист"; fm.ColumnHeading = "Наименование";
                fn.GridColumnWidth = 15 * MM; fm.GridColumnWidth = 160 * MM;
                sd.AddSortGroupField(new ScheduleSortGroupField(fo.FieldId));
                try { sheetList.BodyTextTypeId = t25.Id; sheetList.HeaderTextTypeId = t25.Id; sheetList.TitleTextTypeId = t30.Id; } catch { }
            });
            // sheets (numbers as in the DWG album)
            ElementType vpNoTitle = null;
            Tx(doc, "vp type", delegate
            {
                ElementType vt = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>().First(t => t.FamilyName == "Видовой экран" || t.FamilyName == "Viewport");
                vpNoTitle = (ElementType)vt.Duplicate("КМ_без заголовка");
                vpNoTitle.get_Parameter(BuiltInParameter.VIEWPORT_ATTR_SHOW_LABEL).Set(0);
            });
            string note2 = "1. Общие данные см. на листе 1, спецификацию металлопроката - на листе 2.\r2. Ведомость элементов см. на листе 10.";
            object[][] sh = {
                new object[]{ "1", "Общие данные", "А2", new string[0], "" },
                new object[]{ "2", "Техническая спецификация металла", "А3К", new string[0], "" },
                new object[]{ "3", "Схема расположения закладных деталей", "А3", new[]{ "p3" }, note2 + "\r3. Закладные детали Зд-1, Зд-2 - см. раздел КЖ. Стойки К1, К2 привариваются к закладным деталям, см. узлы 1, 2 на листе 11." },
                new object[]{ "4", "Схема расположения стоек и вертикальных связей", "А3", new[]{ "p4" }, note2 + "\r3. Разрезы 3-3, 4-4 см. на листе 9." },
                new object[]{ "5", "Схема расположения ферм и связей по нижним поясам ферм", "А3", new[]{ "p5" }, note2 + "\r3. Узлы 8, 9 см. на листе 12." },
                new object[]{ "6", "Схема расположения ферм и прогонов по верхним поясам ферм", "А3", new[]{ "p6" }, note2 + "\r3. Прогоны П1 крепить к верхним поясам ферм, см. узел 4 на листе 11." },
                new object[]{ "7", "Разрез 1-1", "А3", new[]{ "1-1" }, note2 + "\r3. Узлы 1-6 см. на листе 11, узлы 7, 14 - на листе 12." },
                new object[]{ "8", "Разрез 2-2", "А3", new[]{ "2-2" }, note2 + "\r3. Узлы см. на листах 11, 12." },
                new object[]{ "9", "Разрезы 3-3, 4-4", "А2", new[]{ "3-3", "4-4" }, note2 + "\r3. Узлы 10-13 см. на листе 12. Положение разрезов см. на листе 4." },
                new object[]{ "10", "Геометрическая схема фермы Ф1 (Ф2). Ведомости элементов", "А2", new[]{ "sФ1", "sФ2", "spec" }, "1. Общие данные см. на листе 1.\r2. Длины элементов приняты по осям расчетной схемы." },
                new object[]{ "11", "Узлы 1...6", "А3", new[]{ "n1", "nа-а", "n2", "nб-б", "n3", "n4", "n5", "n6" }, "" },
                new object[]{ "12", "Узлы 7...14", "А3", new[]{ "n7", "n8", "n9", "n10", "n11", "n12", "n13", "n14" }, "1. Открытые торцы поясов ферм ВП1, НП1 и прогонов П1 закрыть заглушками -t4 (С245) сплошным сварным швом по контуру, см. узлы 7, 14." },
                new object[]{ "13", "Общий вид каркаса", "А3", new[]{ "3d" }, "" } };
            List<ViewSheet> sheets = new List<ViewSheet>();
            Tx(doc, "sheets", delegate
            {
                foreach (object[] s in sh)
                {
                    string fmt = (string)s[2];
                    bool a2 = fmt == "А2", a3k = fmt == "А3К";
                    double W = a2 ? 594 : a3k ? 297 : 420, H = a2 ? 420 : a3k ? 420 : 297;
                    ViewSheet vs = ViewSheet.Create(doc, a2 ? tb2.Id : a3k ? tb3k.Id : tb3.Id);
                    vs.SheetNumber = (string)s[0]; vs.Name = (string)s[1];
                    SetParam(vs, "КМ_Порядок_листа", D((string)s[0]));
                    sheets.Add(vs);
                    if ((string)s[0] == "1") OdSheet(doc, vs, J["od"], t25, t35, tTitle, sheetList, Path.Combine(J["stampdir"], "sig_gip.png"));
                    double sx = W - 5 - 185, sy = 5 - 0.9;
                    Txt(doc, vs.Id, sx + 100, sy + 8.4, (string)s[1], t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 68);
                    Txt(doc, vs.Id, sx + 157.5, sy + 20.9, (string)s[0], t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                    if ((string)s[0] == "1") Txt(doc, vs.Id, sx + 175, sy + 20.9, "13", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                    bool nodeSheet = (string)s[0] == "11" || (string)s[0] == "12";
                    if (((string)s[4]).Length > 0) Txt(doc, vs.Id, nodeSheet ? W - 5 - 185 : 25, nodeSheet ? 80 : 45, (string)s[4], t30, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, nodeSheet ? 183 : Math.Min(W - 25 - 195, 200));
                    double x0 = 25, x1 = W - 10, y0 = 62, y1 = H - 10;
                    string[] vv = (string[])s[3];
                    for (int j = 0; j < vv.Length; j++)
                    {
                        if (vv[j] == "spec") { ScheduleSheetInstance.Create(doc, vs.Id, spec.Id, new XYZ((W - 10 - 185) * MM, (y1 - 10) * MM, 0)); continue; }
                        View vw = vv[j].StartsWith("n") ? (NV.ContainsKey(vv[j].Substring(1)) ? NV[vv[j].Substring(1)] : null) : V[vv[j]];
                        if (vw == null) continue;
                        XYZ c = vv.Length == 1 ? new XYZ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
                            : (string)s[0] == "10" ? new XYZ((x0 + 150) * MM, (j == 0 ? y1 - 80 : y1 - 250) * MM, 0)
                            : new XYZ((x0 + x1) / 2 * MM, (j == 0 ? y1 - (y1 - y0) / 4 : y0 + (y1 - y0) / 4) * MM, 0);
                        Viewport vp = Viewport.Create(doc, vs.Id, vw.Id, c);
                        vp.ChangeTypeId(vpNoTitle.Id);
                        Parameter dn = vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER);
                        try { dn.Set(vv[j].StartsWith("n") ? vv[j].Substring(1).Replace("-", "") : vv[j].Contains("-") ? vv[j].Substring(0, 1) : vv[j]); } catch { }
                    }
                }
            });
            Tx(doc, "special sheets", delegate
            {
                TechSpec(doc, sheets.First(s => s.SheetNumber == "2"), t25, t30);
                foreach (ViewSheet vs in sheets.Where(s => s.SheetNumber == "11" || s.SheetNumber == "12"))
                {
                    doc.Regenerate();
                    List<Viewport> vps = vs.GetAllViewports().Select(id => (Viewport)doc.GetElement(id)).ToList();
                    double x = 25, yTopRow = 287, rowH = 0;
                    foreach (Viewport vp in vps)
                    {
                        Outline ol = vp.GetBoxOutline();
                        double w = (ol.MaximumPoint.X - ol.MinimumPoint.X) / MM, h = (ol.MaximumPoint.Y - ol.MinimumPoint.Y) / MM;
                        if (x + w > 410) { x = 25; yTopRow -= rowH + 18; rowH = 0; }
                        double yc = yTopRow - 16 - h / 2;
                        if (yc - h / 2 < 95 && x + w > 222) { x = 25; yTopRow -= rowH + 18; rowH = 0; yc = yTopRow - 16 - h / 2; }
                        vp.SetBoxCenter(new XYZ((x + w / 2) * MM, yc * MM, 0));
                        L("  vp " + vs.SheetNumber + " " + ((View)doc.GetElement(vp.ViewId)).Name + " " + Math.Round(w) + "x" + Math.Round(h) + " at " + Math.Round(x) + "," + Math.Round(yc));
                        x += w + 12; rowH = Math.Max(rowH, h);
                    }
                }
            });
            // titles: underlined text centred above each drawing (as in the DWG)
            Tx(doc, "titles", delegate
            {
                foreach (ViewSheet vs in sheets)
                    foreach (ElementId vid in vs.GetAllViewports())
                    {
                        Viewport vp = (Viewport)doc.GetElement(vid);
                        View v = (View)doc.GetElement(vp.ViewId);
                        Outline ol = vp.GetBoxOutline();
                        string ttl = v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).AsString() ?? v.Name;
                        double cx = (ol.MinimumPoint.X + ol.MaximumPoint.X) / 2 / MM, ty = ol.MaximumPoint.Y / MM;
                        if (v.Name.StartsWith("Узел "))
                        {
                            string nn = v.Name.Substring(5);
                            Dictionary<string, string> par = new Dictionary<string, string> { { "8", "5" }, { "9", "5" }, { "10", "9" }, { "11", "9" }, { "12", "9" }, { "13", "9" } };
                            string ps = par.ContainsKey(nn) ? par[nn] : "7";
                            XYZ cc = new XYZ(cx * MM, (ty + 9) * MM, 0);
                            doc.Create.NewDetailCurve(vs, Arc.Create(cc, 6 * MM, 0, 2 * Math.PI, XYZ.BasisX, XYZ.BasisY));
                            doc.Create.NewDetailCurve(vs, Line.CreateBound(new XYZ((cx - 6) * MM, (ty + 9) * MM, 0), new XYZ((cx + 6) * MM, (ty + 9) * MM, 0)));
                            Txt(doc, vs.Id, cx, ty + 12, nn, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                            Txt(doc, vs.Id, cx, ty + 6, ps, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                            continue;
                        }
                        TextNote tn = Txt(doc, vs.Id, cx, ty + 4, ttl, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                        FormattedText ft = tn.GetFormattedText(); ft.SetUnderlineStatus(true); tn.SetFormattedText(ft);
                    }
            });
            L("sheets ok");

            try
            {
                ImageExportOptions io = new ImageExportOptions();
                io.ExportRange = ExportRange.SetOfViews;
                io.SetViewsAndSheets(sheets.Select(s => s.Id).ToList());
                io.FilePath = Path.Combine(JobDir, "k2");
                io.ZoomType = ZoomFitType.FitToPage;
                io.PixelSize = 3200;
                io.HLRandWFViewsFileType = ImageFileType.PNG;
                io.ShadowViewsFileType = ImageFileType.PNG;
                io.ImageResolution = ImageResolution.DPI_150;
                doc.ExportImage(io);
            }
            catch (Exception ex) { L("image " + ex.Message); }
            if (J.ContainsKey("pdf"))
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
            SaveAsOptions sao = new SaveAsOptions(); sao.OverwriteExistingFile = true; sao.MaximumBackups = 1;
            doc.SaveAs(outPath, sao);
            doc.Close(false);
            L("saved " + outPath);
            return outPath;
        }
    }
}
