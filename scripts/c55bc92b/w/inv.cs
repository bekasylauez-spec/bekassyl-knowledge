// read-only: browser inventory (views, filters, schedules, materials КМ_*/legacy, families, line weights)
var d = document; var sb = new StringBuilder();
var views = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).ToList();
sb.AppendLine("document " + d.Title + " modified=" + d.IsModified);
sb.AppendLine("views " + views.Count + ": " + string.Join("; ", views.Select(v => v.ViewType + " «" + v.Name + "»")));
sb.AppendLine("РМЦ_ views: " + views.Count(v => v.Name.StartsWith("РМЦ_")) + "; drafting: " + views.Count(v => v.ViewType == ViewType.DraftingView) + "; 3D: " + views.Count(v => v is View3D));
var flt = new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<ParameterFilterElement>().ToList();
sb.AppendLine("filters " + flt.Count + ": " + string.Join(", ", flt.Select(f => f.Name)));
var sch = new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().ToList();
sb.AppendLine("schedules " + sch.Count + ": " + string.Join(", ", sch.Select(s => s.Name)));
var mats = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().ToList();
sb.AppendLine("materials " + mats.Count + "; КМ_/БК_ not КМ_уз_/КМ_<mark> (сталь): " + string.Join(", ", mats.Where(m => (m.Name.StartsWith("КМ_") && !m.Name.StartsWith("КМ_уз_") && !m.Name.EndsWith("(сталь)")) || m.Name.Contains("С245") || m.Name == "Сталь С245").Select(m => m.Name)));
sb.AppendLine("КМ_уз_ materials " + mats.Count(m => m.Name.StartsWith("КМ_уз_")) + ", mark materials " + mats.Count(m => m.Name.EndsWith("(сталь)")));
var fam = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().ToList();
sb.AppendLine("families " + fam.Count + ":");
foreach (var f in fam.OrderBy(x => x.Name)) { int inst = 0; foreach (var sid in f.GetFamilySymbolIds()) inst += new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Count(x => x.Symbol != null && x.Symbol.Id == sid); sb.AppendLine("   " + f.Name + " [" + (f.FamilyCategory == null ? "-" : f.FamilyCategory.Name) + "] types " + f.GetFamilySymbolIds().Count + " inst " + inst + (inst == 0 ? "  <UNUSED>" : "")); }
var cats = d.Settings.Categories;
foreach (var cat in new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds, BuiltInCategory.OST_GenericModel })
{ var c = cats.get_Item(cat); sb.AppendLine("weight «" + c.Name + "»: proj " + c.GetLineWeight(GraphicsStyleType.Projection) + " cut " + c.GetLineWeight(GraphicsStyleType.Cut)); }
var drf = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел");
sb.AppendLine("БК_узел DS by key: " + string.Join(", ", drf.GroupBy(x => (x.ApplicationDataId ?? "").Split('|')[0].Trim()).OrderBy(g => g.Key).Select(g => g.Key + "=" + g.Count())));
sb.AppendLine("DS other: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId != "БК_узел").GroupBy(x => x.ApplicationId).Select(g => g.Key + "=" + g.Count())));
return sb.ToString();
}
static void _end() {
