// Блок 1 before the v3 rebuild: framing by type, DirectShapes, voids, RC geometry, parameters on a member. Read-only.
const double MM = 304.8;
var L = new System.Text.StringBuilder();
L.AppendLine("doc " + document.Title);
var fr = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
L.AppendLine("framing " + fr.Count);
foreach (var g in fr.GroupBy(f => f.Symbol.FamilyName + " :: " + f.Symbol.Name + " [" + f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() + "] mat=" + document.GetElement(f.StructuralMaterialId)?.Name).OrderBy(g => g.Key))
  L.AppendLine("  " + g.Key + ": " + g.Count());
var f0 = fr.First();
L.AppendLine("-- instance params of a member:");
foreach (Parameter p in f0.Parameters) { if (p.Definition == null) continue; string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v)) L.AppendLine("   " + p.Definition.Name + " = " + v); }
L.AppendLine("-- type params:");
foreach (Parameter p in f0.Symbol.Parameters) { if (p.Definition == null) continue; string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v)) L.AppendLine("   " + p.Definition.Name + " = " + v); }
var ds = new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
L.AppendLine("-- directshapes " + ds.Count);
foreach (var g in ds.GroupBy(d => d.Category.Name + " | " + d.Name + " | mark=" + d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() + " | " + d.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString()).OrderBy(g => g.Key).Take(40))
  L.AppendLine("  " + g.Key + ": " + g.Count());
var gm = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToList();
L.AppendLine("-- generic models " + gm.Count + ": " + string.Join("; ", gm.GroupBy(x => x.Name).Select(g => g.Key + " x" + g.Count())));
L.AppendLine("-- RC (ЖБ по АР):");
foreach (var e in new FilteredElementCollector(document).WhereElementIsNotElementType().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("ЖБ")))
{
  var bb = e.get_BoundingBox(null); var ty = document.GetElement(e.GetTypeId());
  string extra = "";
  if (e is Floor) { var fl = (Floor)e; extra = " lvl=" + document.GetElement(fl.LevelId)?.Name + " off=" + Math.Round(fl.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).AsDouble() * MM); }
  if (e is Wall) { var w = (Wall)e; extra = " base=" + document.GetElement(w.LevelId)?.Name + " boff=" + Math.Round(w.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble() * MM) + " h=" + Math.Round(w.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble() * MM); }
  L.AppendLine(string.Format("  {0} {1} [{2}] {3}  bb X {4:F0}..{5:F0} Y {6:F0}..{7:F0} Z {8:F0}..{9:F0}{10}", e.Id, e.Category.Name, ty?.Name, e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString(),
    bb.Min.X * MM, bb.Max.X * MM, bb.Min.Y * MM, bb.Max.Y * MM, bb.Min.Z * MM, bb.Max.Z * MM, extra));
}
L.AppendLine("-- levels: " + string.Join("; ", new FilteredElementCollector(document).OfClass(typeof(Level)).Cast<Level>().OrderBy(l => l.Elevation).Select(l => l.Name + " " + Math.Round(l.Elevation * MM))));
L.AppendLine("-- tube symbols: " + string.Join("; ", new FilteredElementCollector(document).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(s => s.FamilyName.Contains("труба")).Select(s => s.FamilyName + ":" + s.Name + " h=" + Math.Round((s.LookupParameter("h")?.AsDouble() ?? 0) * MM) + " t=" + Math.Round((s.LookupParameter("t")?.AsDouble() ?? 0) * MM, 1))));
L.AppendLine("-- materials КМ_: " + string.Join("; ", new FilteredElementCollector(document).OfClass(typeof(Material)).Cast<Material>().Where(m => m.Name.StartsWith("КМ_")).Select(m => m.Name + " " + m.Color.Red + "," + m.Color.Green + "," + m.Color.Blue)));
L.AppendLine("-- sheets: " + string.Join("; ", new FilteredElementCollector(document).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().OrderBy(s => s.SheetNumber).Select(s => s.SheetNumber + " " + s.Name + " (" + string.Join(", ", s.GetAllPlacedViews().Select(i => document.GetElement(i).Name)) + ")")));
var tb = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().FirstOrDefault();
if (tb != null) { L.AppendLine("-- title block " + document.GetElement(tb.GetTypeId())?.Name + ":"); foreach (Parameter p in tb.Parameters) { if (p.Definition == null) continue; string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v) && v.Length < 80) L.AppendLine("   " + p.Definition.Name + " = " + v); } }
return L.ToString();
