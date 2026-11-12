// READ-ONLY: per-solid bboxes of node DirectShapes + type parameters of member types.
var d = document; double M = 304.8; var sb = new StringBuilder(); var ts = new StringBuilder();
string dir = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\";
try {
  var gopt = new Options { DetailLevel = ViewDetailLevel.Fine };
  sb.AppendLine("id\tdata\tcat\tvol_cm3\tx0\ty0\tz0\tx1\ty1\tz1");
  foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел")) {
    foreach (var g in ds.get_Geometry(gopt)) { var s = g as Solid; if (s == null || s.Volume < 1e-9) continue; var b = s.GetBoundingBox(); var t = b.Transform;
      double x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
      foreach (var px in new[] { b.Min.X, b.Max.X }) foreach (var py in new[] { b.Min.Y, b.Max.Y }) foreach (var pz in new[] { b.Min.Z, b.Max.Z }) { var p = t.OfPoint(new XYZ(px, py, pz)) * M; x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
      sb.AppendLine(ds.Id.Value + "\t" + ds.ApplicationDataId + "\t" + ds.Category.Name + "\t" + (s.Volume * 28316.846592).ToString("0.0") + "\t" + x0.ToString("0") + "\t" + y0.ToString("0") + "\t" + z0.ToString("0") + "\t" + x1.ToString("0") + "\t" + y1.ToString("0") + "\t" + z1.ToString("0")); } }
  System.IO.File.WriteAllText(dir + "solids.tsv", sb.ToString(), Encoding.UTF8);
  foreach (var fs in new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(x => x.Family.Name.StartsWith("(КМ)"))) {
    int n = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Count(x => x.GetTypeId() == fs.Id);
    ts.AppendLine("TYPE " + fs.Family.Name + " : " + fs.Name + " used=" + n);
    foreach (Parameter p in fs.Parameters) { string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v) && p.Definition.Name != "Категория") ts.AppendLine("    " + p.Definition.Name + " = " + v); }
  }
  ts.AppendLine("== instance params sample");
  foreach (var mk in new[] { "К1", "Б1", "Пр1", "ГС1", "Рф1" }) { var f = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().FirstOrDefault(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") == mk); if (f == null) continue; ts.AppendLine("INST " + mk + " id " + f.Id.Value);
    foreach (Parameter p in f.Parameters) { string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v)) ts.AppendLine("    " + p.Definition.Name + " = " + v); } }
  System.IO.File.WriteAllText(dir + "types.txt", ts.ToString(), Encoding.UTF8);
} catch (Exception ex) { return "ERR " + ex; }
return "ok";
