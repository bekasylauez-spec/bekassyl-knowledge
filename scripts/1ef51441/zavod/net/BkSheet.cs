using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Globalization;
using System.Collections.Generic;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;
using AG = Autodesk.AutoCAD.Geometry;
using Multicad;
using Multicad.DatabaseServices;
using Multicad.Symbols;
using MG = Multicad.Geometry;

namespace BkSpds
{
    // Turns one Tekla sheet into the user's SPDS style (ops file from Spds.cs). Positions are kept.
    public class Sheet
    {
        static readonly CultureInfo CI = CultureInfo.InvariantCulture;
        static StringBuilder log = new StringBuilder();
        static double[] N(string s) { return s.Split(' ').Where(x => x != "").Select(x => double.Parse(x, CI)).ToArray(); }
        static MG.Point3d P(double x, double y) { return new MG.Point3d(x, y, 0); }
        static string Env(string n, string d) { return Environment.GetEnvironmentVariable(n) ?? d; }

        const string StampName = "Штамп_В109";
        const string Layer = "БК_Размеры";
        const string AxisLt = "ГОСТ 2.303 5";

        // ---- import the user's stamp block and one SPDS format from the analog DWG ----
        static ObjectId ImportFromAnalog(Database db, string src, bool withBlock)
        {
            ObjectId fmt = ObjectId.Null;
            using (var sdb = new Database(false, true))
            {
                sdb.ReadDwgFile(src, FileShare.ReadWrite, true, null);
                var ids = new ObjectIdCollection();
                using (var tr = sdb.TransactionManager.StartTransaction())
                {
                    var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(sdb), OpenMode.ForRead);
                    // the user's own format (template −3, no built-in title block) is cloned for every sheet
                    if (Env("BK_FMTCLONE", "1") == "1")
                        foreach (ObjectId id in ms)
                            if (id.ObjectClass.Name == "mcsDbObjectFormat") { ids.Add(id); break; }
                    tr.Commit();
                }
                var map = new IdMapping();
                sdb.WblockCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), map, DuplicateRecordCloning.Ignore, false);
                foreach (IdPair p in map) if (ids.Contains(p.Key)) fmt = p.Value;
                // stamp block definition
                var bids = new ObjectIdCollection();
                if (withBlock)
                using (var tr = sdb.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(sdb.BlockTableId, OpenMode.ForRead);
                    if (bt.Has("Штамп№1") && Env("BK_NOBLK", "") == "") bids.Add(bt["Штамп№1"]);
                    var ltt = (LinetypeTable)tr.GetObject(sdb.LinetypeTableId, OpenMode.ForRead);
                    if (ltt.Has(AxisLt) && Env("BK_LTCLONE", "") == "1") bids.Add(ltt[AxisLt]);
                    tr.Commit();
                }
                var map2 = new IdMapping();
                if (bids.Count > 0) sdb.WblockCloneObjects(bids, db.BlockTableId, map2, DuplicateRecordCloning.Ignore, false);
            }
            return fmt;
        }

        static void MakeStamp(Database db, Transaction tr, Dictionary<string, string> data)
        {
            var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForWrite);
            if (bt.Has(StampName)) return;
            var src = (BlockTableRecord)tr.GetObject(bt["Штамп№1"], OpenMode.ForWrite);
            src.Name = StampName;
            MText ауез = null;
            foreach (ObjectId id in src)
            {
                var e = (Entity)tr.GetObject(id, OpenMode.ForWrite);
                if (e is BlockReference) { e.Erase(); continue; }      // foreign signatures
                var mt = e as MText; var tx = e as DBText;
                string s = mt != null ? mt.Contents : tx != null ? tx.TextString : null;
                if (s == null) continue;
                string plain = mt != null ? mt.Text : s;
                string rep = null;
                if (plain.Contains("Олжабаева")) rep = data["gip"];
                else if (plain.Contains("Торебай")) rep = data["check"];
                else if (plain.Contains("Ауез")) { rep = data["dev"]; ауез = mt; }
                else if (plain.Contains("Цех Блок")) rep = data["building"];
                else if (plain.Contains("Строительство завода")) rep = data["object"];
                else if (plain.Contains("Royal")) rep = data["company"];
                else if (plain.Contains("КМ") && plain.Contains("2025")) rep = data["code"];
                else if (plain == "РП") rep = data["stage"];
                if (rep == null) continue;
                if (mt != null) mt.Contents = (mt.Contents.StartsWith("\\pxi") ? mt.Contents.Substring(0, mt.Contents.IndexOf(';') + 1) : "") + rep;
                else tx.TextString = rep;
                if (mt != null && rep == data["code"]) { mt.Contents = rep; mt.Attachment = AttachmentPoint.MiddleCenter; mt.Location = new AG.Point3d(-6000, 4750, 0); mt.Width = 11000; }
                if (mt != null && rep == data["company"]) { mt.Attachment = AttachmentPoint.MiddleLeft; mt.Location = new AG.Point3d(-2900, 750, 0); mt.Width = 2800; }
            }
            if (ауез != null)
            {
                var nc = (MText)ауез.Clone();
                nc.Contents = data["norm"];
                nc.Location = new AG.Point3d(ауез.Location.X, ауез.Location.Y - 500, 0);
                src.AppendEntity(nc); tr.AddNewlyCreatedDBObject(nc, true);
            }
            log.AppendLine("stamp block ready");
        }

        static void EnsureLayer(Database db, Transaction tr)
        {
            var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForWrite);
            if (lt.Has(Layer)) return;
            var l = new LayerTableRecord { Name = Layer };
            lt.Add(l); tr.AddNewlyCreatedDBObject(l, true);
        }

        static void Fin(McEntity e, double k)
        {
            e.DbEntity.AddToCurrentDocument();
            try { e.DbEntity.Scale = k; } catch (System.Exception ex) { log.AppendLine("scale: " + ex.Message); }
            try { e.DbEntity.Layer = Layer; } catch { }
            e.DbEntity.Update();
        }

        [CommandMethod("BKSHEET")]
        public void Run()
        {
            log.Clear();
            var doc = Application.DocumentManager.MdiActiveDocument;
            var db = doc.Database;
            try
            {
                var data = File.ReadAllLines(Env("BK_DATA", ""), Encoding.UTF8).Where(l => l.Contains("=")).ToDictionary(l => l.Substring(0, l.IndexOf('=')), l => l.Substring(l.IndexOf('=') + 1).Replace("\\n", "\\P"));
                var ops = File.ReadAllLines(Env("BK_OPS", ""), Encoding.UTF8);
                ObjectId fmtTpl = ObjectId.Null;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                    bool need = !bt.Has(StampName) && !bt.Has("Штамп№1");
                    tr.Commit();
                    fmtTpl = ImportFromAnalog(db, Env("BK_SRC", ""), need);
                }
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    EnsureLayer(db, tr);
                    MakeStamp(db, tr, data);
                    // erase Tekla objects
                    foreach (var op in ops.Where(o => o.StartsWith("ERASE\t")))
                        foreach (var h in op.Split('\t')[1].Split(' ').Where(x => x != ""))
                        {
                            ObjectId id;
                            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id) && !id.IsErased)
                                tr.GetObject(id, OpenMode.ForWrite).Erase();
                        }
                    tr.Commit();
                }
                double k = 1;
                var only = Env("BK_ONLY", "");
                foreach (var op in ops)
                {
                    var f = op.Split('\t');
                    if (f[0] == "FRAME") k = double.Parse(f[2], CI);
                    if (only != "" && !only.Split(',').Contains(f[0])) continue;
                    try
                    {
                        if (f[0] == "FRAME")
                        {
                            var o = N(f[1]); k = double.Parse(f[2], CI);
                            var fwh = f.Length > 6 ? N(f[6]) : new[] { 841.0, 594.0 };
                            Frame(db, fmtTpl, o[0], o[1], k, f[3], f[4], f[5], data, fwh[0]);
                            fmtTpl = ImportFromAnalog(db, Env("BK_SRC", ""), false);     // a fresh copy for the next frame
                        }
                        else if (f[0] == "AXIS")
                        {
                            var n = N(f[2]);
                            var ax = new McAxisEntity();
                            var lin = ax.Axis.Methods as McBasicAxis.McAxisSpecificLinear;
                            if (lin != null) lin.setPoints(P(n[2], n[3]), P(n[0], n[1]));
                            var mk = ax.Axis.Methods.Markers;
                            try { mk.First.Value = f[1]; } catch { mk.Add(f[1]); }
                            Fin(ax, k);
                            if (lin != null && f.Length > 4)
                            {
                                // put the SPDS marker exactly where the Tekla bubble was
                                var want = N(f[4]);
                                var cen = mk.First.Center;
                                double dx = want[0] - cen.X, dy = want[1] - cen.Y;
                                lin.setPoints(P(n[2], n[3]), P(n[0] + dx, n[1] + dy));
                                ax.DbEntity.Update();
                            }
                            try { ax.DbEntity.LineTypeName = AxisLt; ax.DbEntity.LineTypeScale = Double.Parse(Env("BK_AXLTS", "1"), CI); ax.DbEntity.Update(); }
                            catch (System.Exception ex) { log.AppendLine("axis lt: " + ex.Message); }
                        }
                        else if (f[0] == "MARK")
                        {
                            var n = N(f[2]);
                            var np = new McNotePosition();
                            np.FirstLine = f[1];
                            np.Arrow = (Multicad.Geometry.Arrows)Enum.Parse(np.Arrow.GetType(), "None");
                            np.Origin = P(n[0], n[1]);
                            np.Angle = n[2];
                            Fin(np, k);
                            np.Leader.AddSegment(P(n[3], n[4]), P(n[0], n[1]));
                            np.DbEntity.Update();
                        }
                        else if (f[0] == "CLONEDIMS" || f[0] == "MKBLOCK" || f[0] == "INS" || f[0] == "TXT" || f[0] == "IMPORT" || f[0] == "LINE" || f[0] == "ERASEWIN" || f[0] == "REPL" || f[0] == "CLONEWIN" || f[0] == "PLINE" || f[0] == "DIM")
                            Extra(db, f);
                        else if (f[0] == "XFORM")
                        {
                            var b = N(f[1]); double sc = double.Parse(f[2], CI); var t = N(f[3]);
                            var m = AG.Matrix3d.Displacement(new AG.Vector3d(t[0] - b[0], t[1] - b[1], 0)) * AG.Matrix3d.Scaling(sc, new AG.Point3d(b[0], b[1], 0));
                            using (var tr = db.TransactionManager.StartTransaction())
                            {
                                foreach (var h in f[4].Split(' ').Where(x => x != ""))
                                {
                                    ObjectId id;
                                    if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id) && !id.IsErased)
                                        ((Entity)tr.GetObject(id, OpenMode.ForWrite)).TransformBy(m);
                                }
                                tr.Commit();
                            }
                        }
                        else if (f[0] == "MOVE")
                        {
                            var v = N(f[1]);
                            using (var tr = db.TransactionManager.StartTransaction())
                            {
                                foreach (var h in f[2].Split(' ').Where(x => x != ""))
                                {
                                    ObjectId id;
                                    if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id) && !id.IsErased)
                                        ((Entity)tr.GetObject(id, OpenMode.ForWrite)).TransformBy(AG.Matrix3d.Displacement(new AG.Vector3d(v[0], v[1], 0)));
                                }
                                tr.Commit();
                            }
                        }
                        else if (f[0] == "KNOT")
                        {
                            var n = N(f[3]);
                            var nk = new McNoteKnot();
                            nk.Knot = f[1]; nk.Note = f[2];
                            nk.Center = P(n[0], n[1]); nk.XRadius = n[2]; nk.YRadius = n[2];
                            nk.Rack = P(n[3], n[4]);
                            Fin(nk, k);
                        }
                        else if (f[0] == "SECT")
                        {
                            var n = N(f[2]);
                            var sc = new McSectionVS();
                            sc.Points.Clear(); sc.Points.Add(P(n[0], n[1])); sc.Points.Add(P(n[2], n[3]));
                            sc.Word = f[1];
                            sc.Dir = int.Parse(f[3]);
                            sc.Sheet = -1;
                            var slen = Env("BK_SECLEN", "");
                            if (slen != "") sc.Len = Double.Parse(slen, CI);
                            Fin(sc, k);
                        }
                    }
                    catch (System.Exception ex) { log.AppendLine("op " + f[0] + " " + (f.Length > 1 ? f[1] : "") + ": " + ex.Message); }
                }
                log.AppendLine("done");
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Env("BK_LOG", @"C:\Temp\bksheet.log"), log.ToString(), Encoding.UTF8);
        }

        static bool Inside(Extents3d e, double x0, double x1, double y0, double y1)
        { return e.MinPoint.X >= x0 && e.MaxPoint.X <= x1 && e.MinPoint.Y >= y0 && e.MaxPoint.Y <= y1; }

        // ops for sheets built from pieces: copy dims, make/insert blocks, add text, import a table from another DWG
        static void Extra(Database db, string[] f)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForWrite);
                var msId = bt[BlockTableRecord.ModelSpace];
                var ms = (BlockTableRecord)tr.GetObject(msId, OpenMode.ForWrite);
                if (f[0] == "CLONEDIMS")
                {
                    var n = N(f[1]);      // x0 x1 y0 y1 dx dy
                    var ids = new ObjectIdCollection();
                    foreach (ObjectId id in ms)
                    {
                        if (!id.ObjectClass.IsDerivedFrom(RXObject.GetClass(typeof(Dimension)))) continue;
                        var d = (Dimension)tr.GetObject(id, OpenMode.ForRead);
                        var p = d.TextPosition;
                        if (p.X > n[0] && p.X < n[1] && p.Y > n[2] && p.Y < n[3]) ids.Add(id);
                    }
                    var map = new IdMapping();
                    db.DeepCloneObjects(ids, msId, map, false);
                    var mv = AG.Matrix3d.Displacement(new AG.Vector3d(n[4], n[5], 0));
                    foreach (IdPair pr in map) if (pr.IsPrimary && ids.Contains(pr.Key)) ((Entity)tr.GetObject(pr.Value, OpenMode.ForWrite)).TransformBy(mv);
                    log.AppendLine("dims cloned " + ids.Count);
                }
                else if (f[0] == "MKBLOCK")
                {
                    var n = N(f[2]);      // cx cy hw hh
                    if (!bt.Has(f[1]))
                    {
                        var ids = new ObjectIdCollection();
                        foreach (ObjectId id in ms)
                        {
                            var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                            if (e == null || e is DBText || e is MText || e is Dimension || e is Wipeout || id.ObjectClass.Name.StartsWith("mcs")) continue;
                            Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                            if (Inside(ex, n[0] - n[2], n[0] + n[2], n[1] - n[3], n[1] + n[3])) ids.Add(id);
                        }
                        var btr = new BlockTableRecord { Name = f[1], Origin = AG.Point3d.Origin };
                        var bid = bt.Add(btr); tr.AddNewlyCreatedDBObject(btr, true);
                        var map = new IdMapping();
                        db.DeepCloneObjects(ids, bid, map, false);
                        var mv = AG.Matrix3d.Displacement(new AG.Vector3d(-n[0], -n[1], 0));
                        foreach (IdPair pr in map) if (pr.IsPrimary && ids.Contains(pr.Key)) ((Entity)tr.GetObject(pr.Value, OpenMode.ForWrite)).TransformBy(mv);
                        log.AppendLine("block " + f[1] + " from " + ids.Count + " entities");
                    }
                }
                else if (f[0] == "INS")
                {
                    var n = N(f[2]);
                    var br = new BlockReference(new AG.Point3d(n[0], n[1], 0), bt[f[1]]) { Layer = "0" };
                    ms.AppendEntity(br); tr.AddNewlyCreatedDBObject(br, true);
                }
                else if (f[0] == "TXT")
                {
                    var n = N(f[1]).Concat(N(f[3])).ToArray();      // x y | text | height width attach(1..9)
                    var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                    var mt = new MText { Contents = f[2].Replace("\\n", "\\P"), TextHeight = n[2], Width = n[3], Attachment = (AttachmentPoint)(int)n[4],
                                         Location = new AG.Point3d(n[0], n[1], 0), Layer = "0", TextStyleId = st.Has("ГОСТ 2.304") ? st["ГОСТ 2.304"] : db.Textstyle };
                    ms.AppendEntity(mt); tr.AddNewlyCreatedDBObject(mt, true);
                }
                else if (f[0] == "LINE")
                {
                    // LINE  x1 y1 x2 y2 [lw]  [linetype ltscale]
                    var n = N(f[1]);
                    var ln = new Line(new AG.Point3d(n[0], n[1], 0), new AG.Point3d(n[2], n[3], 0)) { Layer = "0" };
                    if (n.Length > 4) ln.LineWeight = (LineWeight)(int)n[4];
                    if (f.Length > 2 && f[2] != "")
                    {
                        var lp = f[2].Split(' ');
                        var ltt = (LinetypeTable)tr.GetObject(db.LinetypeTableId, OpenMode.ForRead);
                        if (!ltt.Has(lp[0])) { try { db.LoadLineTypeFile(lp[0], "acadiso.lin"); } catch { } }
                        if (ltt.Has(lp[0])) { ln.Linetype = lp[0]; if (lp.Length > 1) ln.LinetypeScale = double.Parse(lp[1], CI); }
                    }
                    ms.AppendEntity(ln); tr.AddNewlyCreatedDBObject(ln, true);
                }
                else if (f[0] == "PLINE")
                {
                    // PLINE  closed lw  |  x y x y ...
                    var h = N(f[1]); var n = N(f[2]);
                    var pl = new Polyline { Layer = "0", Closed = h[0] > 0 };
                    for (int i = 0; i + 1 < n.Length; i += 2) pl.AddVertexAt(i / 2, new AG.Point2d(n[i], n[i + 1]), 0, 0, 0);
                    if (h.Length > 1) pl.LineWeight = (LineWeight)(int)h[1];
                    ms.AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true);
                }
                else if (f[0] == "DIM")
                {
                    // DIM  x1 y1 x2 y2 lx ly rotDeg  |  scale   (the user's «СПДС» style at that scale)
                    var n = N(f[1]); double sc = double.Parse(f[2], CI);
                    var dst = (DimStyleTable)tr.GetObject(db.DimStyleTableId, OpenMode.ForWrite);
                    string nm = "СПДС 1-" + sc.ToString("0", CI);
                    ObjectId sid;
                    if (dst.Has(nm)) sid = dst[nm];
                    else
                    {
                        var src = dst.Has("СПДС") ? (DimStyleTableRecord)tr.GetObject(dst["СПДС"], OpenMode.ForRead) : null;
                        var rec = src != null ? (DimStyleTableRecord)src.Clone() : new DimStyleTableRecord();
                        rec.Name = nm; rec.Dimscale = sc;
                        sid = dst.Add(rec); tr.AddNewlyCreatedDBObject(rec, true);
                    }
                    var d = new RotatedDimension(n[6] * Math.PI / 180, new AG.Point3d(n[0], n[1], 0), new AG.Point3d(n[2], n[3], 0), new AG.Point3d(n[4], n[5], 0), "", sid) { Layer = "0" };
                    ms.AppendEntity(d); tr.AddNewlyCreatedDBObject(d, true);
                }
                else if (f[0] == "CLONEWIN")
                {
                    var n = N(f[1]);      // x0 x1 y0 y1 dx dy
                    var ids = new ObjectIdCollection();
                    foreach (ObjectId id in ms)
                    {
                        var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                        if (e == null || id.ObjectClass.Name.StartsWith("mcs")) continue;
                        Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                        if (Inside(ex, n[0], n[1], n[2], n[3])) ids.Add(id);
                    }
                    var map = new IdMapping();
                    db.DeepCloneObjects(ids, msId, map, false);
                    var mv = AG.Matrix3d.Displacement(new AG.Vector3d(n[4], n[5], 0));
                    foreach (IdPair pr in map) if (pr.IsPrimary && ids.Contains(pr.Key)) ((Entity)tr.GetObject(pr.Value, OpenMode.ForWrite)).TransformBy(mv);
                    log.AppendLine("cloned " + ids.Count);
                }
                else if (f[0] == "ERASEWIN")
                {
                    var n = N(f[1]); int c = 0;
                    foreach (ObjectId id in ms)
                    {
                        var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                        if (e == null) continue;
                        Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                        if (Inside(ex, n[0], n[1], n[2], n[3])) { e.UpgradeOpen(); e.Erase(); c++; }
                    }
                    log.AppendLine("erased in window " + c);
                }
                else if (f[0] == "REPL")
                {
                    var rx = new System.Text.RegularExpressions.Regex(f[1]); int c = 0;
                    foreach (ObjectId id in ms)
                    {
                        var e = tr.GetObject(id, OpenMode.ForRead);
                        var t = e as DBText; var m = e as MText;
                        if (t != null && rx.IsMatch(t.TextString)) { t.UpgradeOpen(); t.TextString = rx.Replace(t.TextString, f[2]); c++; }
                        else if (m != null && rx.IsMatch(m.Contents)) { m.UpgradeOpen(); m.Contents = rx.Replace(m.Contents, f[2]); c++; }
                    }
                    log.AppendLine("replaced " + c + " x " + f[1]);
                }
                else if (f[0] == "IMPORT")
                {
                    // IMPORT  src.dwg  x0 x1 y0 y1 dx dy  skipX0 skipY1  dropRegex
                    var n = N(f[2]);
                    var drop = new System.Text.RegularExpressions.Regex(f[3]);
                    var newIds = new List<ObjectId>();
                    using (var sdb = new Database(false, true))
                    {
                        sdb.ReadDwgFile(f[1], FileShare.ReadWrite, true, null);
                        var ids = new ObjectIdCollection();
                        using (var st = sdb.TransactionManager.StartTransaction())
                        {
                            var sms = (BlockTableRecord)st.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(sdb), OpenMode.ForRead);
                            foreach (ObjectId id in sms)
                            {
                                var cls = id.ObjectClass.Name;
                                if (cls != "AcDbLine" && cls != "AcDbPolyline" && cls != "AcDbText" && cls != "AcDbMText" && cls != "AcDbArc" && cls != "AcDbCircle") continue;
                                var e = (Entity)st.GetObject(id, OpenMode.ForRead);
                                Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                                if (!Inside(ex, n[0], n[1], n[2], n[3])) continue;
                                if (ex.MinPoint.X > n[6] && ex.MaxPoint.Y < n[7]) continue;     // the source stamp
                                string s = e is DBText ? ((DBText)e).TextString : e is MText ? ((MText)e).Text : null;
                                if (s != null && drop.IsMatch(s.Trim())) continue;
                                ids.Add(id);
                            }
                            st.Commit();
                        }
                        var map = new IdMapping();
                        sdb.WblockCloneObjects(ids, msId, map, DuplicateRecordCloning.Ignore, false);
                        foreach (IdPair pr in map) if (pr.IsPrimary && ids.Contains(pr.Key)) newIds.Add(pr.Value);
                    }
                    var mv = AG.Matrix3d.Displacement(new AG.Vector3d(n[4], n[5], 0));
                    foreach (var id in newIds) ((Entity)tr.GetObject(id, OpenMode.ForWrite)).TransformBy(mv);
                    log.AppendLine("imported " + newIds.Count);
                }
                tr.Commit();
            }
        }

        // Цех album as the frame: every sheet keeps its format, stamp, number and name; everything else inside goes
        [CommandMethod("BKCEHCLEAN")]
        public void CehClean()
        {
            log.Clear();
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                var f = new ObjectFilter(); f.AllObjects = true; f.SetCurrentDocument();
                var rects = new List<double[]>();
                foreach (var id in McObjectManager.SelectObjects(f))
                {
                    var fm = id.GetObject() as McFormat;
                    if (fm == null) continue;
                    double s = fm.DbEntity.Scale; double w = fm.Width * s, h = fm.Height * s;
                    rects.Add(new[] { fm.Origin.X, fm.Origin.Y, fm.Origin.X + w, fm.Origin.Y + h, s });
                    log.AppendLine("format " + fm.Format + "x" + fm.Multiplicity + " " + fm.Width + "x" + fm.Height + " s=" + s + " at " + fm.Origin);
                }
                int c = 0;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        if (id.ObjectClass.Name == "mcsDbObjectFormat") continue;
                        var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                        if (e == null) continue;
                        if (e is BlockReference && ((BlockReference)e).Name.StartsWith("Штамп")) continue;
                        Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                        foreach (var r in rects)
                        {
                            if (!Inside(ex, r[0] - 1, r[2] + 1, r[1] - 1, r[3] + 1)) continue;
                            // sheet number and name live in the stamp box
                            bool stampText = (e is DBText || e is MText) && ex.MinPoint.X > r[2] - 190 * r[4] && ex.MaxPoint.Y < r[1] + 60 * r[4];
                            if (!stampText) { e.UpgradeOpen(); e.Erase(); c++; }
                            break;
                        }
                    }
                    tr.Commit();
                }
                log.AppendLine("formats " + rects.Count + ", erased " + c);
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Env("BK_LOG", @"C:\Temp\bkclean.log"), log.ToString(), Encoding.UTF8);
        }

        // one layout per sheet frame: rows "layoutName\tox oy\tk\tW H" (model frame origin, scale, paper size)
        [CommandMethod("BKLAYOUTS")]
        public void Layouts()
        {
            log.Clear();
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                var rows = File.ReadAllLines(Env("BK_SHEETS", ""), Encoding.UTF8).Where(r => r.Trim() != "").Select(r => r.Split('\t')).ToList();
                var lm = LayoutManager.Current;
                Application.SetSystemVariable("LAYOUTCREATEVIEWPORT", 0);
                var keep = new HashSet<string>(rows.Select(r => r[0]));
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var dict = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                    var old = new List<string>();
                    foreach (DBDictionaryEntry de in dict) if (de.Key != "Model") old.Add(de.Key);
                    tr.Commit();
                    lm.CurrentLayout = "Model";
                    foreach (var o in old) { try { lm.DeleteLayout(o); } catch (System.Exception ex) { log.AppendLine("del " + o + ": " + ex.Message); } }
                }
                foreach (var r in rows)
                {
                    var o = N(r[1]); double k = double.Parse(r[2], CI); var wh = N(r[3]);
                    var lid = lm.CreateLayout(r[0]);
                    lm.CurrentLayout = r[0];
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var lay = (Layout)tr.GetObject(lid, OpenMode.ForWrite);
                        var psv = PlotSettingsValidator.Current;
                        psv.SetPlotConfigurationName(lay, "DWG To PDF.pc3", null);
                        psv.RefreshLists(lay);
                        string media = null;
                        foreach (string mname in psv.GetCanonicalMediaNameList(lay))
                            if (mname.StartsWith("ISO_full_bleed_") && mname.Contains("(" + wh[0].ToString("0.00", CI) + "_x_" + wh[1].ToString("0.00", CI) + "_MM)")) { media = mname; break; }
                        if (media == null)
                            foreach (string mname in psv.GetCanonicalMediaNameList(lay))
                                if (mname.StartsWith("ISO_full_bleed_") && mname.Contains("(" + wh[1].ToString("0.00", CI) + "_x_" + wh[0].ToString("0.00", CI) + "_MM)")) { media = mname; break; }
                        if (media != null) psv.SetCanonicalMediaName(lay, media); else log.AppendLine("no media for " + r[0] + " " + r[3]);
                        psv.SetPlotPaperUnits(lay, PlotPaperUnit.Millimeters);
                        psv.SetPlotType(lay, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout);
                        psv.SetUseStandardScale(lay, true); psv.SetStdScaleType(lay, StdScaleType.StdScale1To1);
                        try { psv.SetCurrentStyleSheet(lay, "monochrome.ctb"); } catch { }
                        bool rot = media != null && !media.Contains("(" + wh[0].ToString("0.00", CI) + "_x_");
                        psv.SetPlotRotation(lay, rot ? PlotRotation.Degrees090 : PlotRotation.Degrees000);
                        var ps = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForWrite);
                        bool overall = true;      // the first viewport is the layout's own paper-space viewport: keep it
                        foreach (ObjectId id in ps) { var e = tr.GetObject(id, OpenMode.ForWrite); if (e is Viewport) { if (overall) { overall = false; continue; } e.Erase(); } }
                        var vp = new Viewport();
                        vp.CenterPoint = new AG.Point3d(wh[0] / 2, wh[1] / 2, 0);
                        vp.Width = wh[0] + 1; vp.Height = wh[1] + 1;
                        ps.AppendEntity(vp); tr.AddNewlyCreatedDBObject(vp, true);
                        vp.ViewCenter = new AG.Point2d(o[0] + wh[0] * k / 2, o[1] + wh[1] * k / 2);
                        vp.CustomScale = 1.0 / k;
                        vp.Layer = "Defpoints";
                        vp.On = true; vp.Locked = true;
                        tr.Commit();
                    }
                    log.AppendLine("layout " + r[0]);
                }
                lm.CurrentLayout = rows[0][0];
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Env("BK_LOG", @"C:\Temp\bklayouts.log"), log.ToString(), Encoding.UTF8);
        }

        static void SetLinetype(Database db, McEntity e, string lt, double scale)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var lttab = (LinetypeTable)tr.GetObject(db.LinetypeTableId, OpenMode.ForRead);
                if (lttab.Has(lt))
                {
                    var ent = (Entity)tr.GetObject(new ObjectId(e.ID.ToOldIdPtr()), OpenMode.ForWrite);
                    ent.Linetype = lt; ent.LinetypeScale = scale;
                }
                else log.AppendLine("no linetype " + lt);
                tr.Commit();
            }
        }

        static void Frame(Database db, ObjectId tpl, double ox, double oy, double k, string fmtName, string sheetNo, string sheetName, Dictionary<string, string> data, double fw)
        {
            McFormat fm = null;
            if (!tpl.IsNull)
            {
                var mid = McObjectId.FromOldIdPtr(tpl.OldIdPtr);
                fm = mid.GetObject() as McFormat;
            }
            if (fm == null) { fm = new McFormat(); fm.DbEntity.AddToCurrentDocument(); log.AppendLine("new format (no template)"); }
            bool vertical = fmtName.EndsWith("v");
            var fp = fmtName.TrimEnd('v').Split('x');
            fm.Format = (McFormat.FormatSize)Enum.Parse(typeof(McFormat.FormatSize), fp[0]); fm.Name = fp[0];
            fm.Horizontal = !vertical; fm.Multiplicity = fp.Length > 1 ? int.Parse(fp[1]) : 1;
            try { fm.Template = -3; } catch (System.Exception ex) { log.AppendLine("template: " + ex.Message); }   // as in the user's formats: no built-in title block
            fm.Origin = P(ox, oy);
            try { fm.DbEntity.Scale = k; } catch (System.Exception ex) { log.AppendLine("fmt scale: " + ex.Message); }
            fm.DbEntity.Update();
            log.AppendLine("format " + fm.Format + " W=" + fm.Width + " H=" + fm.Height + " template " + fm.Template + " origin " + fm.Origin);
            if (sheetNo == "Т") return;     // title pages have no stamp, as in the Цех album

            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                double s = k / 100.0;
                double cx = ox + (fw - 5) * k, cy = oy + 5 * k;     // stamp corner = inner frame lower right
                var br = new BlockReference(new AG.Point3d(cx, cy, 0), bt[StampName]) { ScaleFactors = new AG.Scale3d(s), Layer = "0" };
                ms.AppendEntity(br); tr.AddNewlyCreatedDBObject(br, true);
                var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                ObjectId iso = st.Has("Isocpeur") ? st["Isocpeur"] : db.Textstyle;
                var no = new DBText { TextString = sheetNo, Height = 250 * s, TextStyleId = iso, Position = new AG.Point3d(cx - 2957 * s, cy + 1875 * s, 0), Layer = "0" };
                ms.AppendEntity(no); tr.AddNewlyCreatedDBObject(no, true);
                var nm = new MText { Contents = sheetName, TextHeight = 250 * s, TextStyleId = iso, Attachment = AttachmentPoint.MiddleCenter, Width = 6800 * s, Location = new AG.Point3d(cx - 8500 * s, cy + 750 * s, 0), Layer = "0" };
                ms.AppendEntity(nm); tr.AddNewlyCreatedDBObject(nm, true);
                tr.Commit();
            }
        }
    }
}
