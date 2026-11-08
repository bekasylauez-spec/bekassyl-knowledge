var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    sb.AppendLine("docs: " + string.Join(" | ", app.Documents.Cast<Document>().Select(d=>d.PathName)));
    const double M=304.8;
    var ds = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.ApplicationDataId=="база").ToList();
    sb.AppendLine("base DS " + ds.Count);
    foreach (var d in ds.Take(8)) { var b=d.get_BoundingBox(null); sb.AppendLine(d.Name+" id"+d.Id.Value+" min "+Math.Round(b.Min.X*M)+","+Math.Round(b.Min.Y*M)+","+Math.Round(b.Min.Z*M)+" max "+Math.Round(b.Max.X*M)+","+Math.Round(b.Max.Y*M)+","+Math.Round(b.Max.Z*M)); }
    var cols = new FilteredElementCollector(nd).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>().Take(3);
    foreach (var c in cols) { var lp=(LocationPoint)c.Location; var bb=c.get_BoundingBox(null); sb.AppendLine("col "+c.Id.Value+" loc "+Math.Round(lp.Point.X*M)+","+Math.Round(lp.Point.Y*M)+","+Math.Round(lp.Point.Z*M)+" bb z "+Math.Round(bb.Min.Z*M)+".."+Math.Round(bb.Max.Z*M)+" "+ (c.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString())); }
    // bases near origin
    foreach (var d in ds.Where(x=>{var b=x.get_BoundingBox(null); return Math.Abs(b.Min.X*M)<700&&Math.Abs(b.Min.Y*M)<700;})) { var b=d.get_BoundingBox(null); sb.AppendLine("NEAR0 "+d.Name+" "+Math.Round(b.Min.X*M)+","+Math.Round(b.Min.Y*M)+","+Math.Round(b.Min.Z*M)+" -> "+Math.Round(b.Max.X*M)+","+Math.Round(b.Max.Y*M)+","+Math.Round(b.Max.Z*M)); }
    sb.AppendLine("names: " + string.Join("; ", ds.GroupBy(x=>x.Name).Select(g=>g.Key+" "+g.Count())));
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString(), System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static void _end() {
