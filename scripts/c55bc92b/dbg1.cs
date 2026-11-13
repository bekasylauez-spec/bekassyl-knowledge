var d = document; var sb = new System.Text.StringBuilder(); double mm3 = Math.Pow(304.8, 3);
var dsl = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationDataId == "узел 1 | 6-A").ToList();
var fr = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() == "Б1-84").First();
var fs = SolidsOf(fr); sb.AppendLine("Б1-84 solids " + fs.Count + " bbox " + string.Join(",", fs.Select(s => string.Join("/", BBox(s).Select(F)))));
foreach (var ds in dsl) { int k = 0; foreach (var s in SolidsOf(ds)) { double v = 0; string err = ""; foreach (var f in fs) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, f, BooleanOperationsType.Intersect); if (r != null) v += r.Volume * mm3; } catch (Exception ex) { err = ex.Message.Split('\n')[0]; } }
   if (v > 1 || err != "") sb.AppendLine(ds.Name + " #" + k + " vol " + F(s.Volume * mm3) + " bb " + string.Join(",", BBox(s).Select(F)) + " ∩Б1 " + F(v) + " " + err); k++; } }
return sb.ToString();
}
