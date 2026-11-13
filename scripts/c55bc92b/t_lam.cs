var d = document; var sb = new System.Text.StringBuilder(); const double MM = 1 / 304.8; const double S = 175.0 / 5500.0;
var vsym = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "БК_срез_плоскостью");
sb.AppendLine("vsym " + (vsym != null));
using (var t = new Transaction(d, "t")) { t.Start();
  if (!vsym.IsActive) vsym.Activate(); d.Regenerate();
  var view3 = new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().First(v => !v.IsTemplate);
  var Pp = new XYZ(18000 * MM, 18133 * MM, (9293 - S * 133) * MM); var m = new XYZ(0, S, 1).Normalize();
  var e1 = XYZ.BasisX; var e2 = m.CrossProduct(e1).Normalize();
  foreach (bool f in new[] { false, true }) {
    var a1 = f ? e2 : e1; var a2 = f ? e1 : e2;
    var rp = d.Create.NewReferencePlane2(Pp, Pp + a1, a2, view3);
    sb.AppendLine("f=" + f + " rp normal " + rp.Normal + " bubble " + rp.BubbleEnd + " free " + rp.FreeEnd + " m " + m);
    var vi = d.Create.NewFamilyInstance(rp.GetReference(), Pp, a1, vsym); d.Regenerate();
    var tr = vi.GetTransform(); sb.AppendLine("  inst X " + tr.BasisX + " Y " + tr.BasisY + " Z " + tr.BasisZ + " origin " + tr.Origin * 304.8 + " FacingOrientation " + vi.FacingOrientation + " Hand " + vi.HandOrientation);
    var bb = vi.get_BoundingBox(null); sb.AppendLine("  bbox " + bb.Min * 304.8 + " .. " + bb.Max * 304.8);
  }
  t.RollBack(); }
return sb.ToString();
