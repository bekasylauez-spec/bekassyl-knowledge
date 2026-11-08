var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_an.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = An(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static string An(Document nd)
{
  const double M = 304.8; var sb = new System.Text.StringBuilder();
  var fr = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).ToList();
  var L = new List<Tuple<string,XYZ,XYZ,double>>();
  foreach (var f in fr) { if (f.Location is LocationCurve lc) { var c=lc.Curve; string blk=f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; var t=nd.GetElement(f.GetTypeId()); double b = t.LookupParameter("b")?.AsDouble() ?? t.LookupParameter("B")?.AsDouble() ?? 0, h = t.LookupParameter("h")?.AsDouble() ?? t.LookupParameter("H")?.AsDouble() ?? 0; double th=Math.Max(b,h)/2; L.Add(Tuple.Create(blk.Split(' ')[0], c.GetEndPoint(0), c.GetEndPoint(1), th)); } }
  foreach (var mk in new[]{"Пр1","БМ1","БП1"}) {
    var seg = L.Where(x=>x.Item1==mk).ToList(); var stat=new Dictionary<string,int>(); int cnt=0; var ex=new List<string>();
    foreach (var a in seg) foreach (var P in new[]{a.Item2,a.Item3}) {
      var o = seg.FirstOrDefault(y=>!object.ReferenceEquals(y,a) && (y.Item2.DistanceTo(P)<3/M || y.Item3.DistanceTo(P)<3/M)); if(o==null) continue;
      if (a.GetHashCode()>o.GetHashCode()) continue; cnt++;
      string best="none"; double bd=1e9;
      foreach (var q in L) { if (q.Item1==mk) continue; var d=q.Item3-q.Item2; double len=d.GetLength(); var u=d/len; double s=Math.Max(0,Math.Min(len,(P-q.Item2).DotProduct(u))); double dist=(P-q.Item2-u*s).GetLength(); if(dist<bd){bd=dist;best=q.Item1;} }
      string key=best+(bd*M<600?" <600":" >=600"); stat[key]=(stat.ContainsKey(key)?stat[key]:0)+1;
      if(bd*M>=600 && ex.Count<8) ex.Add(Math.Round(P.X*M)+","+Math.Round(P.Y*M)+","+Math.Round(P.Z*M)+" nearest "+best+" "+Math.Round(bd*M));
    }
    sb.AppendLine(mk+" joints "+cnt+": "+string.Join(", ",stat.Select(k=>k.Key+"="+k.Value))+" far: "+string.Join(" ; ",ex));
  }
  var bases = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x=>x.ApplicationId=="БК_узел" && x.ApplicationDataId=="база" && x.Name.StartsWith("База")).Select(x=>x.get_BoundingBox(null)).ToList();
  var cols = fr.Where(x=>x.Location is LocationPoint && x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString().StartsWith("К")==true).ToList();
  int nob=0; var ex2=new List<string>();
  foreach(var c in cols){ var lp=((LocationPoint)c.Location).Point; var bb=c.get_BoundingBox(null); bool ok=bases.Any(b=>lp.X>=b.Min.X-0.01&&lp.X<=b.Max.X+0.01&&lp.Y>=b.Min.Y-0.01&&lp.Y<=b.Max.Y+0.01&&Math.Abs(b.Min.Z-bb.Min.Z)<80/M); if(!ok){nob++; if(ex2.Count<6) ex2.Add(c.Id.Value+" "+Math.Round(lp.X*M)+","+Math.Round(lp.Y*M));} }
  sb.AppendLine("cols "+cols.Count+" plates "+bases.Count+" no plate "+nob+" "+string.Join(";",ex2));
  return sb.ToString();
}
static void _end() {