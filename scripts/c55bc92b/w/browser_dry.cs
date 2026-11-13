// РМЦ КМ q20-түзету (13.11.2026): Project Browser тазалығы — 3602 жобасынан / шаблоннан қалған із (3 drafting көрініс, 8 легаси сүзгі, қолданылмайтын материал, 2 шаблон кестесі, қолданылмайтын (КМ) семействолар),
// агенттер жасаған уақытша көріністер (РМЦ_…), «Несущие колонны» сызық салмағын теңестіру. БК_ аннотация семействолары мен БК_штамп ҚАЛАДЫ. Материал — тек ешбір элемент/тип/дене қолданбаса. Нәтиже қайтарылады (журнал).
// Қолдану: MODE = "DRY" — тек есеп; "DO" — өшіреді. Каркас/узел геометриясына тиіспейді.
return RunBrowser(document);
}
const string MODE = "DRY";
static string RunBrowser(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес";
    bool DO = MODE == "DO";
    // ---- белсенді көріністі {3D}-ға ауыстыру (өшірілетін көріністі белсенді қалдырмау)
    var v3 = new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().FirstOrDefault(v => !v.IsTemplate && v.Name == "{3D}");
    try { var ui = new UIApplication(d.Application); if (v3 != null && ui.ActiveUIDocument != null && ui.ActiveUIDocument.ActiveView.Id != v3.Id) ui.ActiveUIDocument.ActiveView = v3; sb.AppendLine("белсенді көрініс: " + (ui.ActiveUIDocument == null ? "—" : ui.ActiveUIDocument.ActiveView.Name)); } catch (Exception ex) { sb.AppendLine("белсенді көріністі ауыстыру мүмкін болмады: " + ex.Message.Split('\n')[0]); }
    using (var t = new Transaction(d, "РМЦ q20: browser тазалау"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        // ---- 1) көріністер: 3602 drafting (3) + РМЦ_… уақытша
        var drafts = new HashSet<string> { "КМ Узел 1. Крепление кронштейна Кр1 к плите", "КМ Узел 2. Опора стойки", "КМ Узел 3. Примыкание распорки к поясу" };
        var allViews = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).ToList();
        var delV = allViews.Where(v => !(v is ViewSchedule) && v.ViewType != ViewType.ProjectBrowser && v.ViewType != ViewType.SystemBrowser && v.ViewType != ViewType.Internal && v.ViewType != ViewType.Undefined
            && !(v is ViewSheet) && ((v.ViewType == ViewType.DraftingView && drafts.Contains(v.Name)) || v.Name.StartsWith("РМЦ_"))).ToList();
        sb.AppendLine("өшірілетін көрініс: " + delV.Count + " (drafting " + delV.Count(v => drafts.Contains(v.Name)) + ", РМЦ_… " + delV.Count(v => v.Name.StartsWith("РМЦ_")) + ")");
        // ---- 2) легаси сүзгілер (8): барлық көріністен алып, өшіру
        var fnames = new HashSet<string> { "КМ_К1", "КМ_А1", "КМ_Ст1", "КМ_Б1", "КМ_Р1", "КМ_Кр1", "КМ_Кн1", "КМ_Пр1" };
        var filters = new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<ParameterFilterElement>().Where(f => fnames.Contains(f.Name)).ToList();
        int rmF = 0;
        if (DO)
        {
            foreach (var v in allViews) { if (delV.Any(x => x.Id == v.Id)) continue; try { foreach (var fid in v.GetFilters().ToList()) if (filters.Any(f => f.Id == fid)) { v.RemoveFilter(fid); rmF++; } } catch (Exception ex) { sb.AppendLine("  WARN сүзгі алу " + v.Name + ": " + ex.Message.Split('\n')[0]); } }
            int dv = 0; foreach (var v in delV) { try { d.Delete(v.Id); dv++; } catch (Exception ex) { sb.AppendLine("  WARN көрініс өшіру " + v.Name + ": " + ex.Message.Split('\n')[0]); } }
            sb.AppendLine("көрініс өшірілді: " + dv + "/" + delV.Count + "; сүзгі көріністен алынды: " + rmF);
            int df = 0; foreach (var f in filters) { try { d.Delete(f.Id); df++; } catch (Exception ex) { sb.AppendLine("  WARN сүзгі өшіру " + f.Name + ": " + ex.Message.Split('\n')[0]); } }
            sb.AppendLine("сүзгі өшірілді: " + df + "/" + filters.Count);
        }
        else sb.AppendLine("DRY: сүзгі " + filters.Count);
        // ---- 3) шаблон кестелері (2)
        var sch = new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(s => s.Name == "КМ Спецификация металлопроката" || s.Name == "КМ Спецификация пластин").ToList();
        sb.AppendLine("шаблон кестесі: " + string.Join("; ", sch.Select(s => s.Name)));
        if (DO) foreach (var s in sch) { try { d.Delete(s.Id); } catch (Exception ex) { sb.AppendLine("  WARN кесте өшіру: " + ex.Message.Split('\n')[0]); } }
        t.Commit();
    }
    // ---- 4) материалдар: тек ешбір жерде қолданылмаса (тип параметрлері, элемент материалдары, DS беттері)
    var cand = new HashSet<string> { "КМ_А1 (С245)", "КМ_Ст1 (С245)", "КМ_Кн1 (С245)", "КМ_Кр1 (С245)", "КМ_Б1 (С245)", "КМ_К1 (С245)", "КМ_Пр1 (С245)", "КМ_Р1 (С245)", "КМ_анкер", "КМ_пластина", "КМ_шов", "КМ_сталь", "Сталь С245" };
    var mats = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().Where(m => cand.Contains(m.Name)).ToList();
    var candIds = new HashSet<long>(mats.Select(m => m.Id.Value)); var used = new Dictionary<long, string>();
    foreach (var e in new FilteredElementCollector(d).WhereElementIsElementType()) foreach (Parameter p in e.Parameters) { if (p.StorageType != StorageType.ElementId) continue; long id = p.AsElementId().Value; if (candIds.Contains(id) && !used.ContainsKey(id)) used[id] = "тип параметрі: " + e.Name + " / " + p.Definition.Name; }
    foreach (var e in new FilteredElementCollector(d).WhereElementIsNotElementType()) { if (e is Material) continue; ICollection<ElementId> ids = null; try { ids = e.GetMaterialIds(false); } catch { } if (ids != null) foreach (var id in ids) if (candIds.Contains(id.Value) && !used.ContainsKey(id.Value)) used[id.Value] = "элемент: " + e.Name; }
    foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>()) { if (used.Count == candIds.Count) break; foreach (var s in QSolidsOf(ds)) { foreach (Face f in s.Faces) { long id = f.MaterialElementId.Value; if (candIds.Contains(id) && !used.ContainsKey(id)) used[id] = "DS: " + ds.Name; } } }
    foreach (var e in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance))) foreach (var id in e.GetMaterialIds(false)) if (candIds.Contains(id.Value) && !used.ContainsKey(id.Value)) used[id.Value] = "FamilyInstance: " + e.Name;
    var delM = mats.Where(m => !used.ContainsKey(m.Id.Value)).ToList();
    foreach (var m in mats.Where(m => used.ContainsKey(m.Id.Value))) sb.AppendLine("материал ҚАЛДЫ (қолданылады): " + m.Name + " ← " + used[m.Id.Value]);
    sb.AppendLine("материал өшірілетін: " + delM.Count + "/" + cand.Count + " (моделде бар " + mats.Count + "): " + string.Join(", ", delM.Select(m => m.Name)));
    // ---- 5) қолданылмайтын (КМ) семействолар (БК_ аннотация және БК_штамп қалады)
    var fam = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().ToList(); var delFam = new List<Family>();
    foreach (var f in fam)
    {
        if (f.Name.StartsWith("БК_") && !f.Name.StartsWith("БК_КМ_")) continue;        // БК_ аннотация / штамп / срез — қалады
        if (!(f.Name.StartsWith("(КМ)") || f.Name.StartsWith("БК_КМ_"))) continue;
        int inst = 0; foreach (var sid in f.GetFamilySymbolIds()) inst += new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Count(x => x.Symbol != null && x.Symbol.Id == sid);
        if (inst == 0) delFam.Add(f);
    }
    sb.AppendLine("қолданылмайтын семейство: " + string.Join("; ", delFam.Select(f => f.Name)));
    using (var t = new Transaction(d, "РМЦ q20: материал/семейство/салмақ"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        if (DO)
        {
            int n = 0; foreach (var m in delM) { try { d.Delete(m.Id); n++; } catch (Exception ex) { sb.AppendLine("  WARN материал өшіру " + m.Name + ": " + ex.Message.Split('\n')[0]); } }
            sb.AppendLine("материал өшірілді: " + n + "/" + delM.Count);
            n = 0; foreach (var f in delFam) { try { d.Delete(f.Id); n++; } catch (Exception ex) { sb.AppendLine("  WARN семейство өшіру " + f.Name + ": " + ex.Message.Split('\n')[0]); } }
            sb.AppendLine("семейство өшірілді: " + n + "/" + delFam.Count);
        }
        // ---- 6) «Несущие колонны» сызық салмағы = басқа санаттар
        var cats = d.Settings.Categories; var colCat = cats.get_Item(BuiltInCategory.OST_StructuralColumns); var refCat = cats.get_Item(BuiltInCategory.OST_StructuralFraming);
        foreach (var cat in new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds, BuiltInCategory.OST_GenericModel })
        { var c = cats.get_Item(cat); sb.AppendLine("  салмақ «" + c.Name + "»: проекция " + c.GetLineWeight(GraphicsStyleType.Projection) + ", кесу " + c.GetLineWeight(GraphicsStyleType.Cut)); }
        if (DO)
        {
            int wp = refCat.GetLineWeight(GraphicsStyleType.Projection) ?? 1, wc = refCat.GetLineWeight(GraphicsStyleType.Cut) ?? 1;
            colCat.SetLineWeight(wp, GraphicsStyleType.Projection); colCat.SetLineWeight(wc, GraphicsStyleType.Cut);
            sb.AppendLine("«" + colCat.Name + "» салмағы қойылды: проекция " + colCat.GetLineWeight(GraphicsStyleType.Projection) + ", кесу " + colCat.GetLineWeight(GraphicsStyleType.Cut));
        }
        t.Commit();
    }
    if (DO) { d.Save(); sb.AppendLine("saved"); }
    return sb.ToString();
}
class Swallow : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) {
    foreach (var m in a.GetFailureMessages()) if (m.GetSeverity() == FailureSeverity.Warning) a.DeleteWarning(m); return FailureProcessingResult.Continue; } }

