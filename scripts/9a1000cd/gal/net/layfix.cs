using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(LayFix.Cmds))]
namespace LayFix
{
    // %LAYFIX_JSON%: {"ren":[[old,new],..], "del":[names], "jobs":[{n,x0,y0,x1,y1,sc,w,h,media},..]}
    // for every job: layout n (created if missing) gets page setup DWG To PDF.pc3 / media, mm, rot 0, Layout 1:1, origin 0,
    // all model viewports replaced by one viewport = whole page showing the model frame at 1:sc (locked, layer Defpoints)
    public class Cmds
    {
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        [CommandMethod("LAYFIX")]
        public static void Run()
        {
            string jf = Environment.GetEnvironmentVariable("LAYFIX_JSON");
            var log = new StringBuilder();
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                var m = (Dictionary<string, object>)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(jf, Encoding.UTF8));
                var lm = LayoutManager.Current;
                lm.CurrentLayout = "Model";
                if (m.ContainsKey("del")) foreach (var n in (IList)m["del"]) { try { lm.DeleteLayout(n.ToString()); log.AppendLine("deleted " + n); } catch (System.Exception ex) { log.AppendLine("del ERR " + n + ": " + ex.Message); } }
                if (m.ContainsKey("ren")) foreach (var o in (IList)m["ren"]) { var a = (IList)o; try { lm.RenameLayout(a[0].ToString(), a[1].ToString()); log.AppendLine("renamed " + a[0] + " -> " + a[1]); } catch (System.Exception ex) { log.AppendLine("ren ERR " + a[0] + ": " + ex.Message); } }
                int order = 1;
                foreach (Dictionary<string, object> j in (IList)m["jobs"])
                {
                    string n = j["n"].ToString(); string st = "";
                    try
                    {
                        ObjectId lid;
                        try { lid = lm.GetLayoutId(n); if (lid.IsNull) throw new System.Exception("null"); } catch { lid = lm.CreateLayout(n); log.AppendLine("created " + n); }
                        double x0 = D(j["x0"]), y0 = D(j["y0"]), x1 = D(j["x1"]), y1 = D(j["y1"]), sc = D(j["sc"]), w = D(j["w"]), h = D(j["h"]);
                        string media = j["media"].ToString();
                        lm.CurrentLayout = n;   // viewports can only be created/switched on in the current paper space
                        using (var tr = db.TransactionManager.StartTransaction())
                        {
                            var lay = (Layout)tr.GetObject(lid, OpenMode.ForWrite);
                            lay.TabOrder = order++;
                            var v = PlotSettingsValidator.Current;
                            st = "cfg";
                            string dev = "DWG To PDF.pc3", med = media;
                            // prefer an exact custom size on the all-formats device when available
                            string custom = string.Format(IC, "UserDefinedMetric ({0:F2} x {1:F2}мм)", w, h);
                            bool ok = false;
                            try { v.SetPlotConfigurationName(lay, "DWG To PDF_all_formats.pc3", custom); dev = "DWG To PDF_all_formats.pc3"; med = custom; ok = true; } catch { }
                            bool rot90 = false;
                            if (!ok)
                            {   // custom size may exist only as landscape HxW: use it rotated 90
                                string custom2 = string.Format(IC, "UserDefinedMetric ({0:F2} x {1:F2}мм)", h, w);
                                try { v.SetPlotConfigurationName(lay, "DWG To PDF_all_formats.pc3", custom2); dev = "DWG To PDF_all_formats.pc3"; med = custom2; ok = true; rot90 = true; } catch { }
                            }
                            if (!ok) { try { v.SetPlotConfigurationName(lay, dev, media); ok = true; } catch (System.Exception ex) { log.AppendLine(n + " cfg ERR " + ex.Message); } }
                            st = "units"; v.SetPlotPaperUnits(lay, PlotPaperUnit.Millimeters);
                            st = "rot"; v.SetPlotRotation(lay, rot90 ? PlotRotation.Degrees090 : PlotRotation.Degrees000);
                            st = "type"; v.SetPlotType(lay, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout);
                            st = "scale"; v.SetUseStandardScale(lay, true); v.SetStdScaleType(lay, StdScaleType.StdScale1To1);
                            st = "origin"; v.SetPlotOrigin(lay, new Point2d(0, 0));
                            try { v.SetCurrentStyleSheet(lay, "monochrome.ctb"); } catch { }
                            lay.PrintLineweights = true; lay.PlotPlotStyles = true; lay.ScaleLineweights = false;
                            v.RefreshLists(lay);
                            // viewports
                            st = "vps";
                            var btr = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForWrite);
                            bool first = true; int erased = 0;
                            foreach (ObjectId id in btr)
                            {
                                var vp = tr.GetObject(id, OpenMode.ForRead) as Viewport;
                                if (vp == null) continue;
                                if (first) { first = false; continue; }   // paper-space viewport
                                vp.UpgradeOpen(); vp.Erase(); erased++;
                            }
                            var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
                            if (!lt.Has("Defpoints")) { lt.UpgradeOpen(); var lr = new LayerTableRecord { Name = "Defpoints" }; lt.Add(lr); tr.AddNewlyCreatedDBObject(lr, true); }
                            var nv = new Viewport();
                            nv.SetDatabaseDefaults();
                            btr.AppendEntity(nv); tr.AddNewlyCreatedDBObject(nv, true);
                            nv.Layer = "Defpoints";
                            nv.CenterPoint = new Point3d(w / 2, h / 2, 0);
                            nv.Width = w; nv.Height = h;
                            nv.ViewDirection = Vector3d.ZAxis; nv.ViewTarget = Point3d.Origin;
                            nv.ViewCenter = new Point2d((x0 + x1) / 2, (y0 + y1) / 2);
                            nv.ViewHeight = h * sc;
                            nv.TwistAngle = 0;
                            nv.On = true; nv.Locked = true;
                            // layers flagged "freeze in new viewports" would hide dims/frames/tables: thaw everything in this viewport
                            var ids = new ObjectIdCollection(); foreach (ObjectId lid2 in lt) ids.Add(lid2);
                            nv.ThawLayersInViewport(ids.GetEnumerator());
                            // annotation scale of the viewport = 1:sc, else annotative dims/texts/tables stay invisible
                            try
                            {
                                var occ = db.ObjectContextManager.GetContextCollection("ACDB_ANNOTATIONSCALES");
                                AnnotationScale found = null;
                                foreach (ObjectContext oc in occ) { var a = oc as AnnotationScale; if (a != null && Math.Abs(a.DrawingUnits / a.PaperUnits - sc) < 1e-6) { found = a; break; } }
                                if (found == null) { found = new AnnotationScale { Name = "1:" + sc.ToString(IC), PaperUnits = 1, DrawingUnits = sc }; occ.AddContext(found); }
                                nv.AnnotationScale = found;
                            }
                            catch (System.Exception ex) { log.AppendLine(n + " annoscale ERR " + ex.Message); }
                            tr.Commit();
                            log.AppendLine(string.Format(IC, "{0}: {1} / {2}, erased {3} vps, new vp {4}x{5} scale 1:{6} center ({7:F0},{8:F0})", n, dev, med, erased, w, h, sc, (x0 + x1) / 2, (y0 + y1) / 2));
                        }
                    }
                    catch (System.Exception ex) { log.AppendLine(n + " ERR at " + st + ": " + ex.Message); }
                }
                lm.CurrentLayout = "Model";
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(jf + ".log", log.ToString(), Encoding.UTF8);
        }
    }
}
