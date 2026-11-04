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
    // КМ album inside a copy of the user's КЖ template (BI_Шаблон_КЖ): model, mark colours, views, sheets, spec
    public partial class App
    {
        static readonly string[] Marks = { "К1", "К2", "Пк1", "ВП1", "НП1", "Р1", "П1", "РС1", "СГ1", "СВ1", "СВ2", "СВ3", "Зд-1", "Зд-2" };
        static readonly int[][] MarkRgb = {
            new[]{200,30,30}, new[]{150,0,90}, new[]{235,120,0}, new[]{30,80,210}, new[]{0,165,210}, new[]{40,160,60}, new[]{140,60,190},
            new[]{150,95,40}, new[]{225,0,170}, new[]{205,170,0}, new[]{120,145,0}, new[]{0,130,130}, new[]{110,110,110}, new[]{150,150,150} };
        static readonly Dictionary<string, string> MarkName = new Dictionary<string, string> {
            {"К1","Стойка"}, {"К2","Стойка пристройки"}, {"Пк1","Подкос"}, {"ВП1","Пояс верхний фермы"}, {"НП1","Пояс нижний фермы"},
            {"Р1","Решетка фермы"}, {"П1","Прогон"}, {"РС1","Распорка"}, {"СГ1","Связь горизонтальная"}, {"СВ1","Связь вертикальная (ряд М)"},
            {"СВ2","Связь вертикальная (ряд Л)"}, {"СВ3","Связь вертикальная между фермами"} };
        static readonly Dictionary<string, double> KgM = new Dictionary<string, double> {
            {"Труба 140x100x4",14.25}, {"Труба 80x3",7.07}, {"Труба 60x2.5",4.39}, {"Труба 50x2.5",3.60} };

        static T Find<T>(Document d, Func<T, bool> f) where T : Element
        {
            return new FilteredElementCollector(d).OfClass(typeof(T)).Cast<T>().FirstOrDefault(f);
        }

        static void DelAll(Document d, IEnumerable<ElementId> ids)
        {
            foreach (ElementId id in ids.ToList())
            {
                try { if (d.GetElement(id) != null) d.Delete(id); } catch { }
            }
        }

        static void SetParam(Element e, string name, object v)
        {
            Parameter p = e.LookupParameter(name);
            if (p == null || p.IsReadOnly) { L("  no param " + name); return; }
            if (v is string) p.Set((string)v);
            else if (v is int) p.Set((int)v);
            else if (v is double) p.Set((double)v);
        }

        static string BuildKM(Application app, Dictionary<string, string> J)
        {
            string famDir = J["famdir"];
            Directory.CreateDirectory(famDir);
            List<string[]> rows = File.ReadAllLines(J["model"], Encoding.UTF8).Where(x => x.Trim().Length > 0).Select(x => x.Split('|')).ToList();

            // families first (separate docs)
            Dictionary<string, string> beamRfa = new Dictionary<string, string>(), colRfa = new Dictionary<string, string>();
            HashSet<string> colFams = new HashSet<string>(rows.Where(r => r[0] == "C").Select(r => r[1]));
            HashSet<string> beamFams = new HashSet<string>(rows.Where(r => r[0] == "B").Select(r => r[1]));
            foreach (string[] r in rows.Where(r => r[0] == "F"))
            {
                double b = D(r[2]), h = D(r[3]), t = D(r[4]);
                if (beamFams.Contains(r[1])) beamRfa[r[1]] = MakeBeamFamily(app, J["rftbeam"], famDir, r[1], b, h, t);
                if (colFams.Contains(r[1])) colRfa[r[1]] = MakeColumnFamily(app, J["rftcol"], famDir, r[1] + " (стойка)", b, h, t);
            }
            L("families ok");

            // open the КЖ template detached, save as the КМ model
            OpenOptions oo = new OpenOptions();
            oo.DetachFromCentralOption = DetachFromCentralOption.DetachAndDiscardWorksets;
            Document doc = app.OpenDocumentFile(ModelPathUtils.ConvertUserVisiblePathToModelPath(J["kjtemplate"]), oo);
            string outPath = J["out"];
            SaveAsOptions sao = new SaveAsOptions(); sao.OverwriteExistingFile = true;
            doc.SaveAs(outPath, sao);
            L("template opened and saved as " + outPath);

            // ---------------- cleanup of КЖ content
            Tx(doc, "cleanup sheets/views", delegate
            {
                DelAll(doc, new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).ToElementIds());
                DelAll(doc, new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>()
                    .Where(v => !v.IsTemplate && v.ViewType != ViewType.ProjectBrowser && v.ViewType != ViewType.SystemBrowser && v.ViewType != ViewType.Internal && v.ViewType != ViewType.Undefined
                        && !(v is ViewSchedule && (((ViewSchedule)v).IsTitleblockRevisionSchedule || ((ViewSchedule)v).IsInternalKeynoteSchedule)))
                    .Select(v => v.Id));
            });
            Tx(doc, "cleanup model", delegate
            {
                BuiltInCategory[] cats = { BuiltInCategory.OST_Rebar, BuiltInCategory.OST_AreaRein, BuiltInCategory.OST_PathRein, BuiltInCategory.OST_Walls, BuiltInCategory.OST_Floors,
                    BuiltInCategory.OST_StructuralFoundation, BuiltInCategory.OST_GenericModel, BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming,
                    BuiltInCategory.OST_Lines, BuiltInCategory.OST_Assemblies, BuiltInCategory.OST_HVAC_Zones, BuiltInCategory.OST_RasterImages, BuiltInCategory.OST_Grids, BuiltInCategory.OST_ReferenceLines, BuiltInCategory.OST_CLines };
                foreach (BuiltInCategory c in cats)
                    DelAll(doc, new FilteredElementCollector(doc).OfCategory(c).WhereElementIsNotElementType().ToElementIds());
            });
            L("cleanup done; remaining sheets " + new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).GetElementCount());

            // ---------------- levels, grids, project info
            Level lvBase = null, lvTop = null;
            Tx(doc, "levels", delegate
            {
                List<Level> lv = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation).ToList();
                lvBase = lv[0]; lvTop = lv[1];
                for (int i = 2; i < lv.Count; i++) { try { doc.Delete(lv[i].Id); } catch { } }
                lvBase.Elevation = 870 * MM; lvBase.Name = "01 Низ стоек";
                lvTop.Elevation = 4620 * MM; lvTop.Name = "02 Верх покрытия";
                GridType gt = Find<GridType>(doc, g => g.Name == "(ось)круг_10мм_марка_в_начале");
                foreach (string[] r in rows.Where(r => r[0] == "G"))
                {
                    Grid g = Grid.Create(doc, Line.CreateBound(new XYZ(D(r[4]) * MM, D(r[5]) * MM, 0), new XYZ(D(r[2]) * MM, D(r[3]) * MM, 0)));
                    g.Name = r[1];
                    if (gt != null) g.ChangeTypeId(gt.Id);
                }
                ProjectInfo pi = doc.ProjectInformation;
                SetParam(pi, "Наименование проекта", "«Многоквартирный жилой комплекс со встроенными, встроенно-пристроенными помещениями, расположенный по адресу: обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б, 1-я очередь строительства (без наружных инженерных сетей)»");
                SetParam(pi, "Адрес проекта", "обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б");
                SetParam(pi, "Номер проекта", "3669-1");
                SetParam(pi, "Статус проекта", "РП");
                SetParam(pi, "Наименование здания", "Навес 1 над рампой паркинга");
                SetParam(pi, "Название организации", "ТОО \"RAS Group Project\"");
            });
            L("levels/grids ok");

            // ---------------- shared parameters for the spec
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
                    ExternalDefinitionCreationOptions o = new ExternalDefinitionCreationOptions(p[0], p[1] == "t" ? SpecTypeId.String.Text : SpecTypeId.Number);
                    Definition def = grp.Definitions.Create(o);
                    doc.ParameterBindings.Insert(def, app.Create.NewInstanceBinding(cs), GroupTypeId.Data);
                }
            });
            app.SharedParametersFilename = oldSpf;
            L("params ok");

            // ---------------- model
            Dictionary<string, FamilySymbol> bs = new Dictionary<string, FamilySymbol>(), csym = new Dictionary<string, FamilySymbol>();
            int nb = 0, nc = 0, nerr = 0;
            Tx(doc, "frame", delegate
            {
                foreach (KeyValuePair<string, string> kv in beamRfa) bs[kv.Key] = LoadSym(doc, kv.Value);
                foreach (KeyValuePair<string, string> kv in colRfa) csym[kv.Key] = LoadSym(doc, kv.Value);
                Material steel = Find<Material>(doc, m => m.Name == "Сталь С245");
                foreach (FamilySymbol s in bs.Values.Concat(csym.Values))
                {
                    Parameter p = s.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM);
                    if (steel != null && p != null && !p.IsReadOnly) p.Set(steel.Id);
                }
                foreach (string[] r in rows.Where(r => r[0] == "C"))
                {
                    double x = D(r[3]) * MM, y = D(r[4]) * MM, z1 = D(r[5]) * MM, z2 = D(r[6]) * MM;
                    FamilyInstance fi = doc.Create.NewFamilyInstance(new XYZ(x, y, z1), csym[r[1]], lvBase, StructuralType.Column);
                    fi.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).Set(z1 - lvBase.Elevation);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvTop.Id);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(z2 - lvTop.Elevation);
                    Tag(fi, r[2], r[1], (z2 - z1) / MM / 1000.0, "ЛИРА КЭ " + r[7]);
                    nc++;
                }
                foreach (string[] r in rows.Where(r => r[0] == "B"))
                {
                    try
                    {
                        XYZ a = new XYZ(D(r[3]) * MM, D(r[4]) * MM, D(r[5]) * MM), b = new XYZ(D(r[6]) * MM, D(r[7]) * MM, D(r[8]) * MM);
                        string mk = r[2];
                        bool brace = mk == "Р1" || mk == "СГ1" || mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "Пк1";
                        FamilyInstance fi = doc.Create.NewFamilyInstance(Line.CreateBound(a, b), bs[r[1]], lvBase, brace ? StructuralType.Brace : StructuralType.Beam);
                        StructuralFramingUtils.DisallowJoinAtEnd(fi, 0);
                        StructuralFramingUtils.DisallowJoinAtEnd(fi, 1);
                        Parameter zj = fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION);
                        if (r[9] == "B") { zj.Set((int)ZJustification.Bottom); fi.get_Parameter(BuiltInParameter.Z_OFFSET_VALUE).Set(40 * MM); }
                        else zj.Set((int)ZJustification.Center);
                        Tag(fi, mk, r[1], a.DistanceTo(b) / MM / 1000.0, "ЛИРА КЭ " + r[10]);
                        nb++;
                    }
                    catch (Exception ex) { nerr++; if (nerr < 10) L("beam err " + ex.Message); }
                }
                foreach (string[] r in rows.Where(r => r[0] == "D"))
                {
                    double x = D(r[2]) * MM, y = D(r[3]) * MM, z = D(r[4]) * MM, a = D(r[5]) * MM, b = D(r[6]) * MM, t = D(r[7]) * MM;
                    CurveLoop cl = new CurveLoop();
                    XYZ p1 = new XYZ(x - a / 2, y - b / 2, z - t), p2 = new XYZ(x + a / 2, y - b / 2, z - t), p3 = new XYZ(x + a / 2, y + b / 2, z - t), p4 = new XYZ(x - a / 2, y + b / 2, z - t);
                    cl.Append(Line.CreateBound(p1, p2)); cl.Append(Line.CreateBound(p2, p3)); cl.Append(Line.CreateBound(p3, p4)); cl.Append(Line.CreateBound(p4, p1));
                    Solid so = GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { cl }, XYZ.BasisZ, t);
                    DirectShape ds = DirectShape.CreateElement(doc, new ElementId(BuiltInCategory.OST_GenericModel));
                    ds.SetShape(new List<GeometryObject> { so });
                    try { ds.SetName(r[1]); } catch { }
                    SetP(ds, BuiltInParameter.ALL_MODEL_MARK, r[1]);
                    SetP(ds, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, "Закладная деталь (раздел КЖ)");
                    SetParam(ds, "КМ_Наименование", "Закладная деталь (КЖ)");
                    SetParam(ds, "КМ_Сечение", r[1] == "Зд-1" ? "-18 250x280" : "-12 180x180");
                }
            });
            L("columns " + nc + " framing " + nb + " errors " + nerr);

            // ---------------- mark filters with colours
            Dictionary<string, ElementId> flt = new Dictionary<string, ElementId>();
            ElementId solid = new FilteredElementCollector(doc).OfClass(typeof(FillPatternElement)).Cast<FillPatternElement>().First(f => f.GetFillPattern().IsSolidFill).Id;
            Tx(doc, "filters", delegate
            {
                List<ElementId> cats = new List<ElementId> { new ElementId(BuiltInCategory.OST_StructuralFraming), new ElementId(BuiltInCategory.OST_StructuralColumns), new ElementId(BuiltInCategory.OST_GenericModel) };
                foreach (string mk in Marks)
                {
                    string nm = "КМ_" + mk;
                    ParameterFilterElement old = Find<ParameterFilterElement>(doc, f => f.Name == nm);
                    if (old != null) doc.Delete(old.Id);
                    ElementParameterFilter rule = new ElementParameterFilter(ParameterFilterRuleFactory.CreateEqualsRule(new ElementId(BuiltInParameter.ALL_MODEL_MARK), mk));
                    flt[mk] = ParameterFilterElement.Create(doc, nm, cats, rule).Id;
                }
            });
            L("filters ok");

            // ---------------- views
            ViewFamilyType vtPlan = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.StructuralPlan);
            ViewFamilyType vtSec = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section);
            ViewFamilyType vt3d = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.ThreeDimensional);
            View tplPlan = Find<View>(doc, v => v.IsTemplate && v.Name == "#04_Каркас");
            View tplSec = Find<View>(doc, v => v.IsTemplate && v.Name == "#04_Каркас разрез");
            View tpl3d = Find<View>(doc, v => v.IsTemplate && v.Name == "*00_КЖ_(Марки)_3D_Изоляция элементов");
            L("templates: plan " + (tplPlan != null) + " sec " + (tplSec != null) + " 3d " + (tpl3d != null));

            Dictionary<string, View> V = new Dictionary<string, View>();
            Tx(doc, "views", delegate
            {
                string[][] plans = {
                    new[]{ "КМ_01 Закладные детали_(+0,870)", "Схема расположения закладных деталей", "К1,К2,Зд-1,Зд-2" },
                    new[]{ "КМ_02 Стойки и вертикальные связи_(+0,870)", "Схема расположения стоек и вертикальных связей", "К1,К2,СВ1,СВ2" },
                    new[]{ "КМ_03 Фермы и связи по нижним поясам", "Схема расположения ферм и связей покрытия по нижним поясам ферм навеса", "НП1,СГ1,РС1,СВ3" },
                    new[]{ "КМ_04 Фермы и прогоны по верхним поясам", "Схема расположения ферм и прогонов покрытия по верхним поясам ферм навеса", "ВП1,П1" } };
                foreach (string[] pl in plans)
                {
                    ViewPlan vp = ViewPlan.Create(doc, vtPlan.Id, lvBase.Id);
                    vp.Name = pl[0];
                    if (tplPlan != null) { try { vp.ApplyViewTemplateParameters(tplPlan); } catch (Exception ex) { L("tpl plan " + ex.Message); } }
                    vp.ViewTemplateId = ElementId.InvalidElementId;
                    vp.Scale = 100;
                    PlanViewRange pr = vp.GetViewRange();
                    pr.SetLevelId(PlanViewPlane.TopClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.TopClipPlane, 5000 * MM);
                    pr.SetLevelId(PlanViewPlane.CutPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.CutPlane, 4900 * MM);
                    pr.SetLevelId(PlanViewPlane.BottomClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.BottomClipPlane, -100 * MM);
                    pr.SetLevelId(PlanViewPlane.ViewDepthPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.ViewDepthPlane, -100 * MM);
                    vp.SetViewRange(pr);
                    vp.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(pl[1]);
                    StyleView(doc, vp, flt, solid, pl[2].Split(','));
                    vp.CropBoxActive = true;
                    BoundingBoxXYZ cb = vp.CropBox;
                    cb.Min = new XYZ(-4100 * MM, -4100 * MM, cb.Min.Z); cb.Max = new XYZ(25300 * MM, 11300 * MM, cb.Max.Z);
                    vp.CropBox = cb;
                    vp.CropBoxVisible = false;
                    V[pl[0]] = vp;
                }
                // sections: 1-1 frame Ф1 (x=4350), 2-2 frame Ф2 (x=16450) looking to -X (Л left, М right); 3-3 row М, 4-4 row Л looking to +Y
                V["1-1"] = Sec(doc, vtSec.Id, "1-1", "Разрез 1-1", new XYZ(4350 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, 9600, 0, 5300, 1200, 50);
                V["2-2"] = Sec(doc, vtSec.Id, "2-2", "Разрез 2-2", new XYZ(16450 * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, 8100, 0, 5300, 1200, 50);
                V["3-3"] = Sec(doc, vtSec.Id, "3-3", "Разрез 3-3", new XYZ(0, 7700 * MM, 0), XYZ.BasisX, -1200, 25200, 0, 5300, 900, 100);
                V["4-4"] = Sec(doc, vtSec.Id, "4-4", "Разрез 4-4", new XYZ(0, 400 * MM, 0), XYZ.BasisX, -1200, 25200, 0, 5300, 1500, 100);
                foreach (string k in new[] { "1-1", "2-2", "3-3", "4-4" })
                {
                    if (tplSec != null) { try { V[k].ApplyViewTemplateParameters(tplSec); } catch (Exception ex) { L("tpl sec " + ex.Message); } }
                    V[k].ViewTemplateId = ElementId.InvalidElementId;
                    V[k].Scale = (k == "1-1" || k == "2-2") ? 50 : 100;
                    StyleView(doc, V[k], flt, solid, null);
                    try { V[k].SetCategoryHidden(new ElementId(BuiltInCategory.OST_Sections), true); } catch { }
                    V[k].CropBoxVisible = false;
                }
                View3D v3 = View3D.CreateIsometric(doc, vt3d.Id);
                v3.Name = "КМ_3D Навес 1 над рампой";
                if (tpl3d != null) { try { v3.ApplyViewTemplateParameters(tpl3d); } catch (Exception ex) { L("tpl 3d " + ex.Message); } }
                v3.ViewTemplateId = ElementId.InvalidElementId;
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

            // ---------------- annotations (grid dims, frame spacing, tags) — all on model views
            Tx(doc, "annot", delegate
            {
                DimensionType dt = Find<DimensionType>(doc, t => t.StyleType == DimensionStyleType.Linear && t.Name == "BI_основной_2,5мм");
                List<Grid> grids = new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>().ToList();
                List<Grid> gx = grids.Where(g => Math.Abs(((Line)g.Curve).Direction.Y) > 0.9).OrderBy(g => g.Curve.GetEndPoint(0).X).ToList();
                List<Grid> gy = grids.Where(g => Math.Abs(((Line)g.Curve).Direction.X) > 0.9).OrderBy(g => g.Curve.GetEndPoint(0).Y).ToList();
                List<FamilyInstance> colsL = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>()
                    .Where(c => Math.Abs(((LocationPoint)c.Location).Point.Y) < 0.01).OrderBy(c => ((LocationPoint)c.Location).Point.X).ToList();
                foreach (string k in V.Keys.Where(k => k.StartsWith("КМ_0")).ToList())
                {
                    View v = V[k];
                    try
                    {
                        ReferenceArray ra = new ReferenceArray(); foreach (Grid g in gx) ra.Append(new Reference(g));
                        Dimension d1 = doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1400 * MM, 0), new XYZ(1, -1400 * MM, 0)), ra);
                        ReferenceArray ro = new ReferenceArray(); ro.Append(new Reference(gx.First())); ro.Append(new Reference(gx.Last()));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -2000 * MM, 0), new XYZ(1, -2000 * MM, 0)), ro);
                        ReferenceArray rl = new ReferenceArray(); foreach (Grid g in gy) rl.Append(new Reference(g));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(-1900 * MM, 0, 0), new XYZ(-1900 * MM, 1, 0)), rl);
                        ReferenceArray rc = new ReferenceArray();
                        foreach (FamilyInstance c in colsL) rc.Append(c.GetReferences(FamilyInstanceReferenceType.CenterLeftRight).First());
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, 10200 * MM, 0), new XYZ(1, 10200 * MM, 0)), rc);
                        ReferenceArray rco = new ReferenceArray(); rco.Append(rc.get_Item(0)); rco.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, 10800 * MM, 0), new XYZ(1, 10800 * MM, 0)), rco);
                        if (dt != null) foreach (Dimension dd in new FilteredElementCollector(doc, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>()) dd.ChangeTypeId(dt.Id);
                    }
                    catch (Exception ex) { L("dims " + k + " " + ex.Message); }
                }
                // vertical dims in sections 1-1/2-2 between the column ends is left to the level heads (+0,870 / +4,620)
            });
            L("annot ok");

            // marks: one tag per mark per view, placed at the element midpoint
            Tx(doc, "tags", delegate
            {
                FamilySymbol tagBeam = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault(s => s.FamilyName == "(марка)балка");
                FamilySymbol tagCol = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumnTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault(s => s.FamilyName == "(марка)несущая_колонна");
                foreach (FamilySymbol s in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>()) L("  framing tag type " + s.FamilyName + " : " + s.Name);
                FamilySymbol tb2 = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault(s => s.FamilyName == "(марка)балка" && s.Name.StartsWith("Марка"));
                if (tb2 != null) tagBeam = tb2;
                L("tag types " + (tagBeam != null ? tagBeam.Name : "-") + " / " + (tagCol != null ? tagCol.Name : "-"));
                foreach (string k in V.Keys.Where(k => k.StartsWith("КМ_0")).ToList())
                {
                    View v = V[k];
                    HashSet<string> done = new HashSet<string>();
                    foreach (Element e in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().Where(e => e.Category != null && (e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)))
                    {
                        string mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString();
                        if (mk == null || done.Contains(mk) || !Visible(v, flt, mk)) continue;
                        XYZ p = e.Location is LocationCurve ? ((LocationCurve)e.Location).Curve.Evaluate(0.5, true) : ((LocationPoint)e.Location).Point;
                        try
                        {
                            bool col = e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns;
                            FamilySymbol ts = col ? tagCol : tagBeam;
                            if (ts == null) continue;
                            IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), true, TagOrientation.Horizontal, new XYZ(p.X + 500 * MM, p.Y + 500 * MM, 0));
                            done.Add(mk);
                        }
                        catch (Exception ex) { L("tag " + mk + " " + ex.Message); }
                    }
                }
            });
            L("tags ok");

            // ---------------- spec schedule
            ViewSchedule spec = null;
            Tx(doc, "spec", delegate
            {
                spec = ViewSchedule.CreateSchedule(doc, ElementId.InvalidElementId);
                spec.Name = "Спецификация металлопроката";
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
                fMark.ColumnHeading = "Марка"; fName.ColumnHeading = "Наименование"; fSec.ColumnHeading = "Сечение, ГОСТ 30245-2012"; fCnt.ColumnHeading = "Кол-во, шт";
                fLen.ColumnHeading = "Длина общая, м"; fKgm.ColumnHeading = "Масса 1 м, кг"; fMass.ColumnHeading = "Масса общая, кг";
                fLen.DisplayType = ScheduleFieldDisplayType.Totals; fMass.DisplayType = ScheduleFieldDisplayType.Totals;
                sd.AddFilter(new ScheduleFilter(fMass.FieldId, ScheduleFilterType.GreaterThan, 0.0));
                ScheduleField fOrd = sd.AddField(sf["КМ_Порядок"]); fOrd.IsHidden = true;
                sd.AddSortGroupField(new ScheduleSortGroupField(fOrd.FieldId));
                sd.AddSortGroupField(new ScheduleSortGroupField(fMark.FieldId));
                double[] wmm = { 15, 58, 30, 15, 22, 18, 24 };
                ScheduleField[] ff = { fMark, fName, fSec, fCnt, fLen, fKgm, fMass };
                for (int i = 0; i < ff.Length; i++) ff[i].GridColumnWidth = wmm[i] * MM;
                sd.IsItemized = false;
                sd.ShowGrandTotal = true; sd.ShowGrandTotalTitle = true; sd.GrandTotalTitle = "Итого";
                View tplS = Find<View>(doc, v => v.IsTemplate && v.Name == "*(спецификация)стандартный");
                L("spec fields ok, template " + (tplS != null));
            });
            L("spec ok");

            // ---------------- sheets (Форма 3)
            FamilySymbol tb = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().Cast<FamilySymbol>().First(s => s.FamilyName == "(основная_надпись)" && s.Name == "Форма 3");
            ElementType vpType = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>().FirstOrDefault(t => t.Name == "загаловок_на_листе");
            List<ViewSheet> sheets = new List<ViewSheet>();
            Tx(doc, "sheets", delegate
            {
                object[][] sh = {
                    new object[]{ "1", "Схема расположения закладных деталей", 3 },
                    new object[]{ "2", "Схема расположения стоек и вертикальных связей", 3 },
                    new object[]{ "3", "Схема расположения ферм и связей по нижним поясам ферм", 3 },
                    new object[]{ "4", "Схема расположения ферм и прогонов по верхним поясам ферм", 3 },
                    new object[]{ "5", "Разрез 1-1", 3 },
                    new object[]{ "6", "Разрез 2-2", 3 },
                    new object[]{ "7", "Разрезы 3-3, 4-4", 3 },
                    new object[]{ "8", "Общий вид каркаса", 3 },
                    new object[]{ "9", "Спецификация металлопроката", 3 } };
                foreach (object[] s in sh)
                {
                    ViewSheet vs = ViewSheet.Create(doc, tb.Id);
                    vs.SheetNumber = (string)s[0];
                    vs.Name = (string)s[1];
                    sheets.Add(vs);
                    FamilyInstance tbi = new FilteredElementCollector(doc, vs.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilyInstance>().First();
                    SetParam(tbi, "Формат А", (int)s[2]); SetParam(tbi, "Кратность", 1);
                    SetParam(tbi, "Фамилия ГИП", "Казангапов А");
                    SetParam(vs, "BI_штамп_раздел_проекта", "КМ");
                    string[][] who = { new[] { "ГИП", "Казангапов А" }, new[] { "ГАП", "Хасанова К" }, new[] { "Разработал", "Ауез Б" }, new[] { "Проверил", "" }, new[] { "Н.контроль", "Приколотов" } };
                    for (int i = 0; i < who.Length; i++)
                    {
                        SetParam(vs, "BI_штамп_строка_" + (i + 1) + "_должность", who[i][0]);
                        SetParam(vs, "BI_штамп_строка_" + (i + 1) + "_фамилия", who[i][1]);
                    }
                }
            });
            Tx(doc, "viewports", delegate
            {
                object[][] sh = {
                    new object[]{ new[]{ "КМ_01 Закладные детали_(+0,870)" } }, new object[]{ new[]{ "КМ_02 Стойки и вертикальные связи_(+0,870)" } },
                    new object[]{ new[]{ "КМ_03 Фермы и связи по нижним поясам" } }, new object[]{ new[]{ "КМ_04 Фермы и прогоны по верхним поясам" } },
                    new object[]{ new[]{ "1-1" } }, new object[]{ new[]{ "2-2" } }, new object[]{ new[]{ "3-3", "4-4" } }, new object[]{ new[]{ "3d" } }, new object[]{ new[]{ "spec" } } };
                for (int i = 0; i < sheets.Count; i++)
                {
                    ViewSheet vs = sheets[i];
                    FamilyInstance tbi = new FilteredElementCollector(doc, vs.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilyInstance>().First();
                    BoundingBoxXYZ bb = tbi.get_BoundingBox(vs);
                    L("sheet " + vs.SheetNumber + " tb " + Math.Round(bb.Min.X / MM) + "," + Math.Round(bb.Min.Y / MM) + " - " + Math.Round(bb.Max.X / MM) + "," + Math.Round(bb.Max.Y / MM));
                    // drawing area: frame minus 20 mm left binding, 5 mm margins, stamp 185x55 at the bottom right
                    double x0 = bb.Min.X + 25 * MM, x1 = bb.Max.X - 10 * MM, y0 = bb.Min.Y + 60 * MM, y1 = bb.Max.Y - 10 * MM;
                    string[] vv = (string[])sh[i][0];
                    for (int j = 0; j < vv.Length; j++)
                    {
                        XYZ c;
                        if (vv[j] == "spec") c = new XYZ(x0 + 10 * MM, y1 - 10 * MM, 0);
                        else if (vv.Length == 1) c = new XYZ((x0 + x1) / 2, (y0 + y1) / 2, 0);
                        else c = new XYZ((x0 + x1) / 2, j == 0 ? y1 - (y1 - y0) / 4 : y0 + (y1 - y0) / 4, 0);
                        try
                        {
                            if (vv[j] == "spec") { ScheduleSheetInstance.Create(doc, vs.Id, spec.Id, c); continue; }
                            Viewport vp = Viewport.Create(doc, vs.Id, V[vv[j]].Id, c);
                            if (vpType != null) vp.ChangeTypeId(vpType.Id);
                            doc.Regenerate();
                            // title centred above the drawing, like the КМ sheets
                            Outline ol = vp.GetBoxOutline();
                            double w = ol.MaximumPoint.X - ol.MinimumPoint.X, h = ol.MaximumPoint.Y - ol.MinimumPoint.Y;
                            string ttl = V[vv[j]].get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).AsString() ?? V[vv[j]].Name;
                            double len = (ttl.Length * 2.9 + 6) * MM;
                            vp.LabelLineLength = len;
                            vp.LabelOffset = new XYZ(Math.Max(0, (w - len) / 2), h + 3 * MM, 0);
                        }
                        catch (Exception ex) { L("viewport " + vs.SheetNumber + " " + vv[j] + " " + ex.Message); }
                    }
                }
            });
            L("sheets ok");
            try { FixStamp(doc, J.ContainsKey("logo") ? J["logo"] : ""); L("stamp ok"); } catch (Exception ex) { L("stamp " + ex); }

            // ---------------- images for checking, then save
            try
            {
                ImageExportOptions io = new ImageExportOptions();
                io.ExportRange = ExportRange.SetOfViews;
                io.SetViewsAndSheets(sheets.Select(s => s.Id).Concat(new[] { V["3d"].Id }).ToList());
                io.FilePath = Path.Combine(JobDir, "km");
                io.ZoomType = ZoomFitType.FitToPage;
                io.PixelSize = 3200;
                io.HLRandWFViewsFileType = ImageFileType.PNG;
                io.ShadowViewsFileType = ImageFileType.PNG;
                io.ImageResolution = ImageResolution.DPI_150;
                doc.ExportImage(io);
            }
            catch (Exception ex) { L("image " + ex.Message); }
            doc.Save();
            doc.Close(false);
            L("saved " + outPath);
            return outPath;
        }

        static bool Visible(View v, Dictionary<string, ElementId> flt, string mk)
        {
            ElementId id;
            if (!flt.TryGetValue(mk, out id) || !v.IsFilterApplied(id)) return true;
            return v.GetFilterVisibility(id);
        }

        static void Tag(Element e, string mark, string sec, double lenM, string comment)
        {
            SetP(e, BuiltInParameter.ALL_MODEL_MARK, mark);
            SetP(e, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, comment);
            Parameter bm = e.LookupParameter("BI_марка_конструкции");
            if (bm != null && !bm.IsReadOnly && bm.StorageType == StorageType.String) bm.Set(mark);
            string n;
            SetParam(e, "КМ_Наименование", MarkName.TryGetValue(mark, out n) ? n : "");
            SetParam(e, "КМ_Сечение", "□" + sec.Replace("Труба ", "").Replace("x", "х"));
            double kg = KgM.ContainsKey(sec) ? KgM[sec] : 0;
            SetParam(e, "КМ_Длина_м", Math.Round(lenM, 3));
            SetParam(e, "КМ_Масса_1м_кг", kg);
            SetParam(e, "КМ_Масса_кг", Math.Round(lenM * kg, 2));
            SetParam(e, "КМ_Порядок", (double)(Array.IndexOf(Marks, mark) + 1));
        }

        // colour every mark; hide marks not listed in 'show' (null = show all)
        static void StyleView(Document doc, View v, Dictionary<string, ElementId> flt, ElementId solid, string[] show)
        {
            foreach (BuiltInCategory c in new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_GenericModel,
                BuiltInCategory.OST_Grids, BuiltInCategory.OST_Levels, BuiltInCategory.OST_Dimensions, BuiltInCategory.OST_StructuralFramingTags, BuiltInCategory.OST_StructuralColumnTags, BuiltInCategory.OST_Sections })
            {
                try { v.SetCategoryHidden(new ElementId(c), false); } catch { }
            }
            ShowBraces(doc, v);
            foreach (ElementId f in v.GetFilters().ToList()) { if (!flt.Values.Contains(f)) { try { v.RemoveFilter(f); } catch { } } }
            v.DetailLevel = ViewDetailLevel.Fine;
            // SPDS: no line between the two section end marks
            foreach (BuiltInCategory sc0 in new[] { BuiltInCategory.OST_Sections, BuiltInCategory.OST_Viewers }) { try { OverrideGraphicSettings so = new OverrideGraphicSettings(); so.SetProjectionLineColor(new Color(255, 255, 255)); v.SetCategoryOverrides(new ElementId(sc0), so); } catch { } }
            for (int i = 0; i < Marks.Length; i++)
            {
                string mk = Marks[i];
                Color col = new Color((byte)MarkRgb[i][0], (byte)MarkRgb[i][1], (byte)MarkRgb[i][2]);
                OverrideGraphicSettings o = new OverrideGraphicSettings();
                o.SetProjectionLineColor(col);
                o.SetSurfaceForegroundPatternId(solid);
                o.SetSurfaceForegroundPatternColor(col);
                o.SetCutLineColor(col);
                o.SetCutForegroundPatternId(solid);
                o.SetCutForegroundPatternColor(col);
                if (!v.IsFilterApplied(flt[mk])) v.AddFilter(flt[mk]);
                v.SetFilterOverrides(flt[mk], o);
                if (show != null) v.SetFilterVisibility(flt[mk], show.Contains(mk));
            }
        }

        // section box: origin on the cut plane, 'right' = screen right, looking along -(right x Z); u0..u1 / z0..z1 in mm, depth behind the cut
        static ViewSection Sec(Document doc, ElementId typeId, string name, string title, XYZ origin, XYZ right, double u0, double u1, double z0, double z1, double depth, int scale)
        {
            // Revit draws BasisX to the screen LEFT here (checked on the first export), so BasisX = -right
            XYZ bx = right.Negate();
            Transform t = Transform.Identity;
            t.Origin = origin;
            t.BasisX = bx;
            t.BasisY = XYZ.BasisZ;
            t.BasisZ = bx.CrossProduct(XYZ.BasisZ);
            BoundingBoxXYZ box = new BoundingBoxXYZ();
            box.Transform = t;
            double o = right.X > 0.5 ? origin.X : origin.Y;
            box.Min = new XYZ(-(u1 * MM - o), z0 * MM, -depth * MM);
            box.Max = new XYZ(-(u0 * MM - o), z1 * MM, 0);
            ViewSection vs = ViewSection.CreateSection(doc, typeId, box);
            vs.Name = name;
            vs.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(title);
            vs.Scale = scale;
            return vs;
        }
    }
}
