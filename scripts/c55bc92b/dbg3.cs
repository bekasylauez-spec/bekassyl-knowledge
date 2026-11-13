var d = document; var sb = new System.Text.StringBuilder();
var fr = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().First(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() == "Б3-62");
var fs = SolidsOf(fr);
foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationDataId == "узел 2 | 2-D" && x.Name.Contains("ребро ригеля"))) { int k = 0; foreach (var s in SolidsOf(ds)) {
  var bb = BBox(s); string line = "rib#" + k + " bb " + string.Join(",", bb.Select(F)) + " vol " + F(Cu(s.Volume));
  for (int j = 0; j < fs.Count; j++) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, fs[j], BooleanOperationsType.Intersect); line += " | Б3#" + j + " direct " + F(r == null ? 0 : Cu(r.Volume)); } catch { bool a, b; line += " | Б3#" + j + " FAIL est " + F(OvlVol(s, fs[j], out a, out b)); } }
  sb.AppendLine(line); k++; } }
return sb.ToString();
}
