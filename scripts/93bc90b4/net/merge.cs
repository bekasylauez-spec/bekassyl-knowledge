using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(KmMerge.Cmd))]

namespace KmMerge
{
    class PCopy { public double x0, y0, x1, y1, dx, dy; }
    class Sheet
    {
        public string src, name, media; public double ox, oy;
        public List<PCopy> pc = new List<PCopy>();
    }

    public class Cmd
    {
        static StreamWriter log;
        static void L(string s) { log.WriteLine(s); log.Flush(); }

        [CommandMethod("KMMERGE")]
        public void Run()
        {
            string conf = Environment.GetEnvironmentVariable("KMMERGE_CONF");
            var lines = File.ReadAllLines(conf, Encoding.UTF8);
            var sheets = new List<Sheet>();
            string outPath = null, logo = null; double lu = 0, lv = 0;
            foreach (var raw in lines)
            {
                var p = raw.Split('|');
                if (p[0] == "SHEET") sheets.Add(new Sheet { src = p[1], name = p[2], media = p[3], ox = D(p[4]), oy = D(p[5]) });
                else if (p[0] == "PCOPY") sheets[sheets.Count - 1].pc.Add(new PCopy { x0 = D(p[1]), y0 = D(p[2]), x1 = D(p[3]), y1 = D(p[4]), dx = D(p[5]), dy = D(p[6]) });
                else if (p[0] == "OUT") outPath = p[1];
                else if (p[0] == "LOGO") { logo = p[1]; lu = D(p[2]); lv = D(p[3]); }
                else if (p[0] == "LOG") log = new StreamWriter(p[1], false, Encoding.UTF8);
            }
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                try { Application.SetSystemVariable("LAYOUTCREATEVIEWPORT", 0); } catch (System.Exception ex) { L("lcv " + ex.Message); }
                int tab = 3;
                foreach (var s in sheets) { DoSheet(db, s, tab++); }
                if (logo != null) FixLogo(db, logo, lu, lv);
                LayoutManager.Current.CurrentLayout = "Model";
                try { Application.SetSystemVariable("IMAGEFRAME", 0); } catch (System.Exception ex) { L("if " + ex.Message); }
                try { Application.SetSystemVariable("WIPEOUTFRAME", 0); } catch (System.Exception ex) { L("wf " + ex.Message); }
                db.SaveAs(outPath, DwgVersion.Current);
                L("SAVED " + outPath);
            }
            catch (System.Exception ex) { L("ERR " + ex); }
            log.Close();
        }

        static double D(string s) { return double.Parse(s, System.Globalization.CultureInfo.InvariantCulture); }

        void DoSheet(Database db, Sheet s, int tab)
        {
            L("== " + s.name);
            var off = new Vector3d(s.ox, s.oy, 0);
            using (var side = new Database(false, true))
            {
                side.ReadDwgFile(s.src, FileShare.Read, true, "");
                side.CloseInput(true);
                var modelIds = new ObjectIdCollection();
                var pcIds = new List<ObjectIdCollection>();
                foreach (var pc in s.pc) pcIds.Add(new ObjectIdCollection());
                ObjectId srcLayoutBtr = ObjectId.Null; ObjectId srcLayoutId = ObjectId.Null;
                var paperIds = new ObjectIdCollection();
                ObjectId overallSrc = ObjectId.Null;
                using (var tr = side.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(side.BlockTableId, OpenMode.ForRead);
                    var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                        int hit = -1;
                        if (s.pc.Count > 0)
                        {
                            try
                            {
                                var ex = e.GeometricExtents;
                                for (int i = 0; i < s.pc.Count; i++)
                                {
                                    var c = s.pc[i];
                                    if (ex.MinPoint.X >= c.x0 && ex.MaxPoint.X <= c.x1 && ex.MinPoint.Y >= c.y0 && ex.MaxPoint.Y <= c.y1) { hit = i; break; }
                                }
                            }
                            catch { }
                        }
                        if (hit >= 0) pcIds[hit].Add(id); else modelIds.Add(id);
                    }
                    var dict = (DBDictionary)tr.GetObject(side.LayoutDictionaryId, OpenMode.ForRead);
                    foreach (DBDictionaryEntry de in dict)
                    {
                        if (de.Key == "Layout1") { srcLayoutId = de.Value; srcLayoutBtr = ((Layout)tr.GetObject(de.Value, OpenMode.ForRead)).BlockTableRecordId; }
                    }
                    var lbtr = (BlockTableRecord)tr.GetObject(srcLayoutBtr, OpenMode.ForRead);
                    foreach (ObjectId id in lbtr)
                    {
                        var e = tr.GetObject(id, OpenMode.ForRead);
                        if (e is Viewport && overallSrc.IsNull) overallSrc = id;
                        paperIds.Add(id);
                    }
                    tr.Commit();
                }
                L("model " + modelIds.Count + " paper " + paperIds.Count + " pcopy " + string.Join(",", pcIds.ConvertAll(c => c.Count.ToString())));

                // 1. model space
                var newModel = new List<ObjectId>();
                ObjectId msId;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                    msId = bt[BlockTableRecord.ModelSpace];
                    tr.Commit();
                }
                var map = new IdMapping();
                side.WblockCloneObjects(modelIds, msId, map, DuplicateRecordCloning.Ignore, false);
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (ObjectId id in modelIds)
                    {
                        var nid = map[id].Value;
                        var e = (Entity)tr.GetObject(nid, OpenMode.ForWrite);
                        e.TransformBy(Matrix3d.Displacement(off));
                        newModel.Add(nid);
                    }
                    tr.Commit();
                }

                // 2. layout
                var lm = LayoutManager.Current;
                ObjectId layId = lm.CreateLayout(s.name);
                ObjectId layBtr;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var lay = (Layout)tr.GetObject(layId, OpenMode.ForWrite);
                    layBtr = lay.BlockTableRecordId;
                    var v = PlotSettingsValidator.Current;
                    v.SetPlotConfigurationName(lay, "DWG To PDF.pc3", s.media);
                    try { v.SetPlotPaperUnits(lay, PlotPaperUnit.Millimeters); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetPlotRotation(lay, PlotRotation.Degrees000); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetPlotType(lay, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetUseStandardScale(lay, true); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetStdScaleType(lay, StdScaleType.StdScale1To1); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetPlotCentered(lay, false); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetPlotOrigin(lay, new Point2d(0, 0)); } catch (System.Exception ex) { L("psv " + ex.Message); }
                    try { v.SetCurrentStyleSheet(lay, "monochrome.ctb"); } catch { }
                    lay.TabOrder = tab;
                    tr.Commit();
                }
                var map2 = new IdMapping();
                side.WblockCloneObjects(paperIds, layBtr, map2, DuplicateRecordCloning.Ignore, false);
                var vps = new List<ObjectId>();
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (ObjectId id in paperIds)
                    {
                        if (id == overallSrc) continue;
                        var nid = map2[id].Value;
                        var vp = tr.GetObject(nid, OpenMode.ForWrite) as Viewport;
                        if (vp != null) { vp.ViewTarget = vp.ViewTarget + off; vps.Add(nid); }
                    }
                    tr.Commit();
                }
                lm.CurrentLayout = s.name;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    int on = 0, num = 0;
                    foreach (var vid in vps) { var v2 = (Viewport)tr.GetObject(vid, OpenMode.ForWrite); v2.On = true; if (v2.On) on++; if (v2.Number > 0) num++; }
                    var b0 = (BlockTableRecord)tr.GetObject(layBtr, OpenMode.ForRead);
                    foreach (ObjectId id in b0) { var v0 = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (v0 == null) continue; L(string.Format("  first vp num={0} c=({1:F1},{2:F1}) w={3:F1} h={4:F1}", v0.Number, v0.CenterPoint.X, v0.CenterPoint.Y, v0.Width, v0.Height)); break; }
                    L("  vps on " + on + " numbered " + num + " of " + vps.Count);
                    tr.Commit();
                }
                // 3. paper copies (L1 notes)
                for (int i = 0; i < s.pc.Count; i++)
                {
                    if (pcIds[i].Count == 0) continue;
                    var m3 = new IdMapping();
                    side.WblockCloneObjects(pcIds[i], layBtr, m3, DuplicateRecordCloning.Ignore, false);
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        foreach (ObjectId id in pcIds[i])
                        {
                            var e = (Entity)tr.GetObject(m3[id].Value, OpenMode.ForWrite);
                            e.TransformBy(Matrix3d.Displacement(new Vector3d(s.pc[i].dx, s.pc[i].dy, 0)));
                        }
                        tr.Commit();
                    }
                    L("pcopy " + i + " -> paper " + pcIds[i].Count);
                }
                // 4. texts clipped by viewport edges -> full copy in paper space
                ClipTexts(db, newModel, vps, layBtr, s);
            }
            LayoutManager.Current.CurrentLayout = "Model";
        }

        void ClipTexts(Database db, List<ObjectId> model, List<ObjectId> vps, ObjectId layBtr, Sheet s)
        {
            // sheet size from media name
            double W = s.media.Contains("A1") ? 841 : 594, H = s.media.Contains("A1") ? 594 : 420;
            int added = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var ps = (BlockTableRecord)tr.GetObject(layBtr, OpenMode.ForWrite);
                // collect texts with world transform
                var texts = new List<KeyValuePair<Entity, Extents3d>>();
                foreach (var id in model)
                {
                    var br = tr.GetObject(id, OpenMode.ForRead) as BlockReference;
                    if (br == null) continue;
                    Collect(tr, br, br.BlockTransform, br, texts);
                }
                foreach (var vid in vps)
                {
                    var vp = (Viewport)tr.GetObject(vid, OpenMode.ForRead);
                    double sc = vp.Height / vp.ViewHeight;
                    var c = vp.CenterPoint;
                    double px0 = c.X - vp.Width / 2, px1 = c.X + vp.Width / 2, py0 = c.Y - vp.Height / 2, py1 = c.Y + vp.Height / 2;
                    if (px1 < 0 || px0 > W || py1 < 0 || py0 > H) continue;
                    var t = vp.ViewTarget + new Vector3d(vp.ViewCenter.X, vp.ViewCenter.Y, 0);
                    double rx0 = t.X - vp.Width / 2 / sc, rx1 = t.X + vp.Width / 2 / sc, ry0 = t.Y - vp.Height / 2 / sc, ry1 = t.Y + vp.Height / 2 / sc;
                    double tol = 0.05 / sc;
                    var m2p = Matrix3d.Displacement(new Vector3d(c.X, c.Y, 0)) * Matrix3d.Scaling(sc, Point3d.Origin) * Matrix3d.Displacement(-t.GetAsVector());
                    foreach (var kv in texts)
                    {
                        var ex = kv.Value;
                        bool overlap = ex.MaxPoint.X > rx0 + tol && ex.MinPoint.X < rx1 - tol && ex.MaxPoint.Y > ry0 + tol && ex.MinPoint.Y < ry1 - tol;
                        bool inside = ex.MinPoint.X >= rx0 - tol && ex.MaxPoint.X <= rx1 + tol && ex.MinPoint.Y >= ry0 - tol && ex.MaxPoint.Y <= ry1 + tol;
                        if (!overlap || inside) continue;
                        var cp = (Entity)kv.Key.Clone();
                        cp.TransformBy(m2p);
                        ps.AppendEntity(cp); tr.AddNewlyCreatedDBObject(cp, true);
                        added++;
                        string str = cp is DBText ? ((DBText)cp).TextString : ((MText)cp).Contents;
                        L(string.Format("  cliptext '{0}' vp({1:F0},{2:F0})", str, c.X, c.Y));
                    }
                }
                tr.Commit();
            }
            L("cliptexts added " + added);
        }

        void Collect(Transaction tr, BlockReference top, Matrix3d xf, BlockReference parent, List<KeyValuePair<Entity, Extents3d>> outL)
        {
            var btr = (BlockTableRecord)tr.GetObject(parent.BlockTableRecord, OpenMode.ForRead);
            foreach (ObjectId id in btr)
            {
                var o = tr.GetObject(id, OpenMode.ForRead);
                if (o is BlockReference) { var b = (BlockReference)o; Collect(tr, top, xf * b.BlockTransform, b, outL); continue; }
                if (!(o is DBText) && !(o is MText)) continue;
                var e = (Entity)((Entity)o).Clone();
                e.TransformBy(xf);
                try { if (e.ColorIndex == 0) e.Color = top.Color; } catch { }
                try { if (((Entity)o).Layer == "0" && top.Layer != "0") e.LayerId = top.LayerId; } catch { }
                try { if (e.LineWeight == LineWeight.ByBlock) e.LineWeight = top.LineWeight; } catch { }
                Extents3d ex;
                try { ex = e.GeometricExtents; } catch { continue; }
                outL.Add(new KeyValuePair<Entity, Extents3d>(e, ex));
            }
        }

        void FixLogo(Database db, string png, double u, double v)
        {
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                // one fresh image definition for the logo
                ObjectId dictId = RasterImageDef.GetImageDictionary(db);
                if (dictId.IsNull) dictId = RasterImageDef.CreateImageDictionary(db);
                var idict = (DBDictionary)tr.GetObject(dictId, OpenMode.ForWrite);
                var nd = new RasterImageDef();
                try { nd.SourceFileName = png; } catch (System.Exception ex) { L("logo src " + ex.Message); }
                try { nd.Load(); } catch (System.Exception ex) { L("logo load " + ex.Message); }
                ObjectId ndId = idict.SetAt("Company_logo", nd);
                tr.AddNewlyCreatedDBObject(nd, true);
                foreach (ObjectId bid in bt)
                {
                    var btr = (BlockTableRecord)tr.GetObject(bid, OpenMode.ForRead);
                    foreach (ObjectId id in btr)
                    {
                        var im = tr.GetObject(id, OpenMode.ForRead) as RasterImage;
                        if (im == null || im.ImageDefId.IsNull) continue;
                        if (im.ImageDefId == ndId) continue;
                        var def = (RasterImageDef)tr.GetObject(im.ImageDefId, OpenMode.ForRead);
                        if (!def.SourceFileName.ToLower().Contains("logo")) continue;
                        im.UpgradeOpen();
                        im.ImageDefId = ndId;
                        try { im.AssociateRasterDef(nd); } catch { }
                        var o = im.Orientation;
                        im.Orientation = new CoordinateSystem3d(o.Origin, new Vector3d(u, 0, 0), new Vector3d(0, v, 0));
                        n++;
                    }
                }
                tr.Commit();
            }
            L("logo fixed " + n);
        }
    }
}
