using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.PlottingServices;

[assembly: CommandClass(typeof(PlotL.Cmds))]
namespace PlotL
{
    // plot every layout (tab order) with its own page setup to %PLOTL_DIR%\<layout>.pdf (console AutoCAD)
    public class Cmds
    {
        [CommandMethod("PLOTL")]
        public static void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument; var db = doc.Database;
            string dir = Environment.GetEnvironmentVariable("PLOTL_DIR");
            var log = new StringBuilder();
            Application.SetSystemVariable("BACKGROUNDPLOT", 0);
            var lays = new List<KeyValuePair<int, string>>();
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                foreach (DBDictionaryEntry en in ld)
                {
                    var lo = (Layout)tr.GetObject(en.Value, OpenMode.ForRead);
                    if (lo.ModelType) continue;
                    lays.Add(new KeyValuePair<int, string>(lo.TabOrder, lo.LayoutName));
                }
                tr.Commit();
            }
            lays.Sort((a, b) => a.Key.CompareTo(b.Key));
            foreach (var kv in lays)
            {
                string n = kv.Value;
                try
                {
                    LayoutManager.Current.CurrentLayout = n;
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var lid = LayoutManager.Current.GetLayoutId(n);
                        var lay = (Layout)tr.GetObject(lid, OpenMode.ForRead);
                        var pi = new PlotInfo { Layout = lid };
                        var piv = new PlotInfoValidator { MediaMatchingPolicy = MatchingPolicy.MatchEnabled };
                        piv.Validate(pi);
                        string outp = Path.Combine(dir, n + ".pdf");
                        using (var pe = PlotFactory.CreatePublishEngine())
                        {
                            pe.BeginPlot(null, null);
                            pe.BeginDocument(pi, doc.Name, null, 1, true, outp);
                            var ppi = new PlotPageInfo();
                            pe.BeginPage(ppi, pi, true, null);
                            pe.BeginGenerateGraphics(null); pe.EndGenerateGraphics(null);
                            pe.EndPage(null); pe.EndDocument(null); pe.EndPlot(null);
                        }
                        tr.Commit();
                        log.AppendLine(n + " ok " + File.Exists(outp) + " " + lay.CanonicalMediaName);
                    }
                }
                catch (System.Exception ex) { log.AppendLine(n + " ERR " + ex.Message); }
            }
            try { LayoutManager.Current.CurrentLayout = "Model"; } catch { }
            File.WriteAllText(Path.Combine(dir, "plotl_log.txt"), log.ToString(), Encoding.UTF8);
        }
    }
}
