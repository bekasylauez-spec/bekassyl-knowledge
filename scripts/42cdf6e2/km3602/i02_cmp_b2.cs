// 3602: what did the 30.10 «ус тест» change in Портал Блок 2? Compare the current file with Архив\…Блок 2_до_БК (29.10 split). Read-only.
var A = @"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\Архив\3602-КМ_Портал Блок 2_до_БК_30.10.2026.rvt";
var B = @"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\Каркастар\3602-КМ_Портал Блок 2.rvt";
var outLog = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\km3602\_cmp_b2.txt";
var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> h = null;
h = (s, e) => {
  uiapp.Idling -= h; var L = new System.Text.StringBuilder(); Document da = null, db = null;
  try {
    // open the archive from a temp copy (never touch the archive file itself)
    var tmp = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "km_cmp_" + Guid.NewGuid().ToString("N") + ".rvt"); System.IO.File.Copy(A, tmp, true);
    da = uiapp.Application.OpenDocumentFile(tmp); db = uiapp.Application.OpenDocumentFile(B);
    Cmp.Run(da, db, L);
    da.Close(false); da = null; try { System.IO.File.Delete(tmp); } catch { }
  } catch (Exception ex) { L.AppendLine("ERR " + ex); }
  finally { try { if (da != null) da.Close(false); } catch { } try { if (db != null) db.Close(false); } catch { } }
  System.IO.File.WriteAllText(outLog, L.ToString(), System.Text.Encoding.UTF8);
};
uiapp.Idling += h; return "queued";
}
public static class Cmp {
  const double MM = 304.8;
  static string Sig(Document d, Element x) {
    var sb = new System.Text.StringBuilder();
    sb.Append(x.GetTypeId().Value).Append('|');
    var lc = x.Location as LocationCurve; if (lc != null) { var c = lc.Curve; var a = c.GetEndPoint(0) * MM; var b = c.GetEndPoint(1) * MM; sb.AppendFormat("{0:F1},{1:F1},{2:F1}>{3:F1},{4:F1},{5:F1}|", a.X, a.Y, a.Z, b.X, b.Y, b.Z); }
    var lp = x.Location as LocationPoint; if (lp != null) { var p = lp.Point * MM; sb.AppendFormat("{0:F1},{1:F1},{2:F1}|", p.X, p.Y, p.Z); }
    var fi = x as FamilyInstance;
    if (fi != null && fi.StructuralType == Autodesk.Revit.DB.Structure.StructuralType.Beam || fi != null && fi.StructuralType == Autodesk.Revit.DB.Structure.StructuralType.Brace) {
      sb.AppendFormat("ext {0:F1}/{1:F1}|", fi.get_Parameter(BuiltInParameter.START_EXTENSION).AsDouble() * MM, fi.get_Parameter(BuiltInParameter.END_EXTENSION).AsDouble() * MM);
      sb.Append("join ").Append(Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 0)).Append('/').Append(Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 1)).Append('|');
      sb.Append("jg ").Append(string.Join(",", JoinGeometryUtils.GetJoinedElements(d, fi).Select(i => d.GetElement(i)?.UniqueId ?? "?").OrderBy(q => q))).Append('|');
    }
    var bb = x.get_BoundingBox(null); if (bb != null) sb.AppendFormat("bb {0:F0},{1:F0},{2:F0};{3:F0},{4:F0},{5:F0}", bb.Min.X * MM, bb.Min.Y * MM, bb.Min.Z * MM, bb.Max.X * MM, bb.Max.Y * MM, bb.Max.Z * MM);
    return sb.ToString();
  }
  public static void Run(Document da, Document db, System.Text.StringBuilder L) {
    Func<Document, Dictionary<string, Element>> map = d => new FilteredElementCollector(d).WhereElementIsNotElementType().Where(x => x.Category != null).GroupBy(x => x.UniqueId).ToDictionary(g => g.Key, g => g.First());
    var ma = map(da); var mb = map(db);
    L.AppendLine("archive elements " + ma.Count + ", current " + mb.Count);
    var onlyA = ma.Keys.Except(mb.Keys).ToList(); var onlyB = mb.Keys.Except(ma.Keys).ToList();
    L.AppendLine("-- only in archive " + onlyA.Count + ":"); foreach (var g in onlyA.Select(k => ma[k]).GroupBy(x => x.Category.Name)) L.AppendLine("   " + g.Key + ": " + g.Count() + "  e.g. " + string.Join(", ", g.Take(4).Select(x => x.Id + " " + x.Name)));
    L.AppendLine("-- only in current " + onlyB.Count + ":"); foreach (var g in onlyB.Select(k => mb[k]).GroupBy(x => x.Category.Name)) L.AppendLine("   " + g.Key + ": " + g.Count() + "  e.g. " + string.Join(", ", g.Take(4).Select(x => x.Id + " " + x.Name)));
    int nd = 0;
    L.AppendLine("-- changed model elements (type/location/ext/join/bbox):");
    foreach (var k in ma.Keys.Intersect(mb.Keys)) {
      var xa = ma[k]; var xb = mb[k]; if (xa.Category.CategoryType != CategoryType.Model) continue;
      var sa = Sig(da, xa); var sb2 = Sig(db, xb); if (sa == sb2) continue;
      if (nd++ < 40) { L.AppendLine("   " + xb.Id + " " + xb.Category.Name + " " + xb.Name); L.AppendLine("      A: " + sa); L.AppendLine("      B: " + sb2); }
    }
    L.AppendLine("changed total " + nd);
    // views
    Func<Document, IEnumerable<string>> vw = d => new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).Select(v => v.ViewType + ": " + v.Name);
    L.AppendLine("-- views archive: " + string.Join("; ", vw(da))); L.AppendLine("-- views current: " + string.Join("; ", vw(db)));
  }
}
static void Pad() {
