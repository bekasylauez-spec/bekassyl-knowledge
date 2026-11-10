}
public class BKLoad : IFamilyLoadOptions {
    public bool OnFamilyFound(bool inUse, out bool ov) { ov = true; return true; }
    public bool OnSharedFamilyFound(Family f, bool inUse, out FamilySource src, out bool ov) { src = FamilySource.Family; ov = true; return true; } }
public static class BKStyle
{
    public static void Setup(Document d, string dir, System.Text.StringBuilder sb)
    {
        const double MM = 1 / 304.8;
        // 1 families (overwrite: the shelf leader and the section mark differ from the ones in БК_КМ.rte)
        foreach (var f in new[] { "БК_типовая_аннотация_текст_с_выноской", "БК_марка_разрез", "БК_узел_круг", "БК_обрыв", "БК_шов_заводской", "БК_шов_монтажный", "БК_шов_угол", "БК_знак_разреза" })
        {
            string p = System.IO.Path.Combine(dir, f + ".rfa"); if (!System.IO.File.Exists(p)) { sb.AppendLine("MISSING file " + p); continue; }
            Family fam; bool r = d.LoadFamily(p, new BKLoad(), out fam); sb.AppendLine("family " + f + ": " + (r ? "loaded" : "already the same"));
        }
        d.Regenerate();
        // the base types come from БК_КМ.rte / БК_КМ_узлы.rte: without them the project is not a БК project — stop with a clear line instead of an exception
        var need = new[] { "БК_заголовок_на_листе", "БК_основной_2,5мм", "БК_текст_2,5" }.Where(n => !new FilteredElementCollector(d).OfClass(typeof(ElementType)).Any(x => x.Name == n)).ToList();
        if (!new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().Any(x => x.ViewFamily == ViewFamily.Section && x.Name == "БК_разрез")) need.Add("БК_разрез (section type)");
        if (need.Count > 0) { sb.AppendLine("MISSING base types: " + string.Join(", ", need) + " — the project is not made from БК_КМ.rte; copy them with «Копировать стандарты проекта» from БК_КМ_узлы.rte, then run again"); return; }
        Func<string, ElementType> T =n => new FilteredElementCollector(d).OfClass(typeof(ElementType)).Cast<ElementType>().FirstOrDefault(x => x.Name == n);
        Func<string, string, FamilySymbol> Sy = (f, n) => new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.Family.Name == f && x.Name == n);
        // 2 thin open arrow 3.5 mm / 20°
        var arrow = T("БК_стрелка_открытая_3,5мм_20°");
        if (arrow == null) { var a0 = new FilteredElementCollector(d).OfClass(typeof(ElementType)).Cast<ElementType>().First(x => x.FamilyName == "Засечка" && x.get_Parameter(BuiltInParameter.ARROW_TYPE) != null && x.get_Parameter(BuiltInParameter.ARROW_TYPE).AsInteger() == (T("БК_стрелка_открытая_1,5мм_90°") ?? x).get_Parameter(BuiltInParameter.ARROW_TYPE).AsInteger() && x.Name.StartsWith("БК_стрелка")); arrow = a0.Duplicate("БК_стрелка_открытая_3,5мм_20°"); }
        arrow.get_Parameter(BuiltInParameter.ARROW_FILLED).Set(0); arrow.get_Parameter(BuiltInParameter.ARROW_CLOSED).Set(0);
        arrow.get_Parameter(BuiltInParameter.ARROW_SIZE).Set(3.5 * MM); arrow.get_Parameter(BuiltInParameter.LEADER_ARROW_WIDTH).Set(20 * Math.PI / 180);
        // 3 leader types: plain (bolt notes, no arrow) and «БК_выноска_стрелка»
        var ldPlain = Sy("БК_типовая_аннотация_текст_с_выноской", "БК_типовая_аннотация_текст_с_выноской");
        var ldArrow = Sy("БК_типовая_аннотация_текст_с_выноской", "БК_выноска_стрелка") ?? (ldPlain.Duplicate("БК_выноска_стрелка") as FamilySymbol);
        ldArrow.get_Parameter(BuiltInParameter.LEADER_ARROWHEAD).Set(arrow.Id); ldPlain.get_Parameter(BuiltInParameter.LEADER_ARROWHEAD).Set(ElementId.InvalidElementId);
        sb.AppendLine("leader types: «" + ldPlain.Name + "» (no arrow), «" + ldArrow.Name + "» (arrow " + arrow.Name + ")");
        // 4 viewport without a title (node view, 3D picture)
        var vp0 = T("БК_заголовок_на_листе"); var vpX = T("БК_без_заголовка") ?? vp0.Duplicate("БК_без_заголовка"); vpX.get_Parameter(BuiltInParameter.VIEWPORT_ATTR_SHOW_LABEL).Set(0);
        // 5 section tags: number beside the arrow — head «спереди», tail «сзади»; a second section type for reference sections with an empty reference label
        var front = Sy("БК_марка_разрез", "БК_марка_разрез_номер_вида_спереди_3,5мм"); var back = Sy("БК_марка_разрез", "БК_марка_разрез_номер_вида_сзади_3,5мм");
        var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.Section && x.Name == "БК_разрез");
        var tag = d.GetElement(vft.get_Parameter(BuiltInParameter.SECTION_TAG).AsElementId()) as ElementType;
        tag.get_Parameter(BuiltInParameter.SECTION_ATTR_HEAD_TAG).Set(front.Id); tag.get_Parameter(BuiltInParameter.SECTION_ATTR_TAIL_TAG).Set(back.Id);
        var tag2 = T("БК_разрез_номер_вида_на_фасаде") ?? tag.Duplicate("БК_разрез_номер_вида_на_фасаде");
        tag2.get_Parameter(BuiltInParameter.SECTION_ATTR_HEAD_TAG).Set(front.Id); tag2.get_Parameter(BuiltInParameter.SECTION_ATTR_TAIL_TAG).Set(back.Id);
        var vft2 = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().FirstOrDefault(x => x.Name == "БК_разрез_на_фасаде") ?? (vft.Duplicate("БК_разрез_на_фасаде") as ViewFamilyType);
        vft2.get_Parameter(BuiltInParameter.SECTION_TAG).Set(tag2.Id); vft2.get_Parameter(BuiltInParameter.VIEWER_REFERENCE_LABEL_TEXT).Set("");
        sb.AppendLine("section types: «БК_разрез» (live sections), «БК_разрез_на_фасаде» (reference sections, empty label); tags head спереди / tail сзади");
        // 6 materials dull (3D picture without glare)
        int nm = 0; foreach (var m in new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().Where(x => x.Name.StartsWith("КМ_"))) { m.Shininess = 0; m.Smoothness = 0; nm++; }
        sb.AppendLine("КМ_ materials dull: " + nm);
        // 7 what must already be in the project (from БК_КМ.rte)
        foreach (var n in new[] { "БК_основной_2,5мм", "БК_текст_2,5", "БК_заголовок_на_листе" }) sb.AppendLine("type " + n + ": " + (T(n) != null ? "ok" : "MISSING"));
        sb.AppendLine("title block БК_штамп: " + (new FilteredElementCollector(d).OfClass(typeof(Family)).Any(x => x.Name == "БК_штамп") ? "ok" : "MISSING"));
    }
}
static void Dummy() {
