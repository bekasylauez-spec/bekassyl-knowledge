var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_f.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var ds = nd.GetElement(new ElementId(3887835L)) as DirectShape; sb.AppendLine(ds.Name + " / " + ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString());
    foreach (var so in Solids(ds)) { var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max); sb.AppendLine("  weld bbox " + P(a) + ".." + P(b) + " vol " + Math.Round(so.Volume / (MM*MM*MM))); }
    var c = Solids(ds).Select(q => q.ComputeCentroid()).First();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")))
    { var bb = f.get_BoundingBox(null); if (bb == null) continue; if (bb.Min.X - 20*MM < c.X && bb.Max.X + 20*MM > c.X && bb.Min.Y - 40*MM < c.Y && bb.Max.Y + 40*MM > c.Y && bb.Min.Z - 40*MM < c.Z && bb.Max.Z + 40*MM > c.Z) sb.AppendLine("  near " + (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString()) + " bbox " + P(bb.Min) + ".." + P(bb.Max)); }
    int n = 0; foreach (var d in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.Name.StartsWith("шов решётки"))) n++; sb.AppendLine("lattice weld DS " + n);
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString(), System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static string P(XYZ p) { return "(" + Math.Round(p.X / MM, 1) + "," + Math.Round(p.Y / MM, 1) + "," + Math.Round(p.Z / MM, 1) + ")"; }
