var d = document; var sb = new System.Text.StringBuilder();
var all = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") != "").ToList();
Func<string, FamilyInstance> byMark = m => all.First(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == m);
var b1 = byMark("Б1-54"); var sl = SolidsOf(b1);
sb.AppendLine("Б1-54 solids " + sl.Count + " vol " + Math.Round(sl.Sum(s => s.Volume) * Math.Pow(304.8, 3)));
double self = 0; foreach (var a in sl) foreach (var b in sl) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); if (r != null) self += r.Volume; } catch (Exception ex) { sb.AppendLine("err " + ex.Message); } }
sb.AppendLine("self-intersect (all pairs) " + Math.Round(self * Math.Pow(304.8, 3)));
// Б1-54 vs a copy moved by 100 mm in X (partial overlap check): use Transform
var tr = Transform.CreateTranslation(new XYZ(100 / 304.8, 0, 0)); double part = 0;
foreach (var a in sl) foreach (var b in sl) { var bm = SolidUtils.CreateTransformed(b, tr); try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, bm, BooleanOperationsType.Intersect); if (r != null) part += r.Volume; } catch (Exception ex) { sb.AppendLine("err2 " + ex.Message); } }
sb.AppendLine("intersect with copy shifted 100 mm " + Math.Round(part * Math.Pow(304.8, 3)));
return sb.ToString();
}
static List<Solid> SolidsOf(Element e) { var r = new List<Solid>(); foreach (var go in e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine })) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
    r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r;
