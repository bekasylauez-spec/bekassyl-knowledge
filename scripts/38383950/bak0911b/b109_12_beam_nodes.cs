// Завод В109 Цех Блок 1: rolled-section nodes from beamnodes.tsv (nodes.py): caps, fins −10 + bolts М16, column stiffeners −14, СФ caps,
// БП2 ridge splice, Р2 fins, purlin bolts, КН welds, БМ1 bearing ribs + bolts М20, площадка fins. Run with -Lib b109_lib.cs. Key «балки».
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\_b109_12.txt";
string tsv = @"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\beamnodes.tsv";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); sb.Append(Build(nd, tsv)); nd.Save(); sb.AppendLine("saved"); }
  catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}

static double Nm(string s) { return double.Parse(s, System.Globalization.CultureInfo.InvariantCulture); }
static string Build(Document d, string tsv)
{
    var sb = new System.Text.StringBuilder(); int nb = 0, nw = 0, np = 0, ng = 0;
    var rows = System.IO.File.ReadAllLines(tsv, System.Text.Encoding.UTF8).Where(l => l.Trim().Length > 0).Select(l => l.Split('\t')).ToList();
    using (var t = new Transaction(d, "В109: узлы балок"))
    {
        t.Start();
        var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        sb.AppendLine("removed " + RemoveNode(d, "балки") + " old pieces");
        var soP = SoPlate(d); var soB = SoBolt(d); var soW = SoWeld(d);
        foreach (var g in rows.GroupBy(r => r[1]))
        {
            var plates = new List<GeometryObject>(); var bolts = new List<GeometryObject>(); var welds = new List<GeometryObject>();
            foreach (var r in g)
            {
                if (r[0] == "BOX")
                {
                    double x0 = Nm(r[2]), y0 = Nm(r[3]), z0 = Nm(r[4]), x1 = Nm(r[5]), y1 = Nm(r[6]), z1 = Nm(r[7]);
                    if (x1 - x0 < 0.5 || y1 - y0 < 0.5 || z1 - z0 < 0.5) continue;
                    plates.Add(Plate(P(x0, y0, z0), XYZ.BasisX, XYZ.BasisY, Rect(0, 0, x1 - x0, y1 - y0), z1 - z0, false, soP)); np++;
                }
                else if (r[0] == "PLT")
                {
                    var o = P(Nm(r[2]), Nm(r[3]), Nm(r[4])); var eu = new XYZ(Nm(r[5]), Nm(r[6]), Nm(r[7])).Normalize(); var ev = new XYZ(Nm(r[8]), Nm(r[9]), Nm(r[10])).Normalize();
                    plates.Add(Plate(o, eu, ev, Rect(Nm(r[11]), Nm(r[12]), Nm(r[13]), Nm(r[14])), Nm(r[15]), false, soP)); np++;
                }
                else if (r[0] == "BOLT")
                {
                    var c = P(Nm(r[2]), Nm(r[3]), Nm(r[4])); var u = new XYZ(Nm(r[5]), Nm(r[6]), Nm(r[7])).Normalize(); int dia = (int)Nm(r[8]); double grip = Nm(r[9]);
                    bolts.AddRange(Bolt(c, u, dia, grip, BoltLen(dia, grip), soB)); nb++;
                }
                else if (r[0] == "WELD")
                {
                    var o = P(Nm(r[2]), Nm(r[3]), Nm(r[4])); var a = new XYZ(Nm(r[5]), Nm(r[6]), Nm(r[7])); var b = new XYZ(Nm(r[8]), Nm(r[9]), Nm(r[10])); var dv = new XYZ(Nm(r[11]), Nm(r[12]), Nm(r[13]));
                    double kf = Nm(r[14]), len = Nm(r[15]); if (len < 1) continue;
                    welds.Add(Weld(o, a.Normalize(), b.Normalize(), dv.Normalize(), kf, len, soW)); nw++;
                }
            }
            string nm = g.Key;
            if (plates.Count > 0) DS(d, BuiltInCategory.OST_StructConnections, "балки", nm, plates);
            if (bolts.Count > 0) DS(d, BuiltInCategory.OST_StructConnectionBolts, "балки", "Болт " + nm, bolts);
            if (welds.Count > 0) DS(d, BuiltInCategory.OST_StructConnectionWelds, "балки", "шов " + nm, welds);
            ng++;
        }
        t.Commit();
    }
    sb.AppendLine("groups " + ng + ", plates " + np + ", bolts " + nb + ", welds " + nw);
    return sb.ToString();
}
