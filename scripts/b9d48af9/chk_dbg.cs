var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_dbg.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Dbg(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static string Pt(XYZ p) { return "(" + Math.Round(p.X / MM, 1) + "," + Math.Round(p.Y / MM, 1) + "," + Math.Round(p.Z / MM, 1) + ")"; }
static string Dbg(Document nd)
{
    var sb = new System.Text.StringBuilder();
    foreach (var ds in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts))
    { var bb = ds.get_BoundingBox(null); if (bb == null) continue; if (bb.Min.X / MM < 6300 && bb.Max.X / MM > 5900 && bb.Min.Y / MM < 100 && bb.Max.Y / MM > -100 && bb.Max.Z / MM > 14000 && bb.Min.Z / MM < 14600)
      { sb.AppendLine("DS#" + ds.Id.Value + " " + ds.Name + " bbox " + Pt(bb.Min) + ".." + Pt(bb.Max));
        foreach (var s in Solids(ds)) { CylindricalFace cf = null; foreach (Face f in s.Faces) { cf = f as CylindricalFace; if (cf != null) break; } if (cf == null) continue; double r = cf.get_Radius(0).GetLength() / MM; var b2 = s.GetBoundingBox(); if (r > 9 && r < 13 || r > 7 && r < 9) sb.AppendLine("   cyl R" + Math.Round(r, 1) + " ax " + Pt(cf.Axis) + " org " + Pt(cf.Origin) + " vol " + Math.Round(s.Volume / (MM * MM * MM))); } } }
    return sb.ToString();
}