using System;
using System.Linq;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Multicad;
using Multicad.DatabaseServices;

[assembly: CommandClass(typeof(MC4.Cmds))]
namespace MC4
{
    // SPDS edits in full AutoCAD, jobs from %TEMP%\mc4_job.txt, one per line:
    //   stretchY <handle> <yAbove> <yNew>   move every stretch point with y > yAbove to y = yNew
    public class Cmds
    {
        [CommandMethod("MC4REN")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var log = new StringBuilder();
            string tmp = Environment.GetEnvironmentVariable("TEMP");
            var IC = System.Globalization.CultureInfo.InvariantCulture;
            try
            {
                foreach (var line in File.ReadAllLines(Path.Combine(tmp, "mc4_job.txt")))
                {
                    if (line.StartsWith("noteReplace|"))
                    {
                        // noteReplace|old|new : replace text in FirstLine/SecondLine of every SPDS note in model space
                        var q = line.Split('|');
                        int n = 0;
                        using (var tr = db.TransactionManager.StartTransaction())
                        {
                            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                            foreach (ObjectId nid in ms)
                            {
                                if (!nid.ObjectClass.DxfName.StartsWith("SPDSNOTE")) continue;
                                using (var mc = McObjectManager.GetObject(McObjectId.FromOldIdPtr(nid.OldIdPtr)))
                                {
                                    if (mc == null) continue;
                                    foreach (var pn in new[] { "FirstLine", "SecondLine" })
                                    {
                                        var pi = mc.GetType().GetProperty(pn);
                                        if (pi == null || !pi.CanWrite) continue;
                                        var s = Convert.ToString(pi.GetValue(mc, null));
                                        if (s == null || !s.Contains(q[1])) continue;
                                        pi.SetValue(mc, s.Replace(q[1], q[2]), null);
                                        var me = mc as McEntity; if (me != null) me.DbEntity.Update();
                                        n++;
                                        log.AppendLine("  note " + nid.Handle + " " + pn + " '" + s + "'");
                                    }
                                }
                            }
                            tr.Commit();
                        }
                        log.AppendLine("noteReplace '" + q[1] + "' -> '" + q[2] + "': " + n);
                        continue;
                    }
                    if (line.StartsWith("ser "))
                    {
                        // ser <handle> : dump the serialized SPDS object to %TEMP%\ser_<handle>.bin
                        var h = line.Substring(4).Trim();
                        ObjectId sid;
                        if (!db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out sid)) { log.AppendLine("no " + h); continue; }
                        using (var mc = McObjectManager.GetObject(McObjectId.FromOldIdPtr(sid.OldIdPtr)))
                        {
                            var me = mc as McEntity;
                            byte[] b = me.DbEntity.SerializeToBytes();
                            File.WriteAllBytes(Path.Combine(tmp, "ser_" + h + ".bin"), b);
                            log.AppendLine("ser " + h + " " + b.Length);
                        }
                        continue;
                    }
                    var todo = new System.Collections.Generic.List<string>();
                    if (line.StartsWith("levelAll|"))
                    {
                        // levelAll|old|new : every SPDS level mark in model space whose serialized text contains old
                        var q0 = line.Split('|');
                        var pat = Encoding.GetEncoding(28591).GetBytes(q0[1]);
                        var hits = new System.Collections.Generic.List<ObjectId>();
                        using (var tr = db.TransactionManager.StartTransaction())
                        {
                            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                            foreach (ObjectId nid in ms) if (nid.ObjectClass.DxfName.StartsWith("SPDSLEVEL")) hits.Add(nid);
                            tr.Commit();
                        }
                        foreach (var nid in hits)
                        {
                            byte[] bb;
                            using (var mc = McObjectManager.GetObject(McObjectId.FromOldIdPtr(nid.OldIdPtr)))
                            { var me = mc as McEntity; if (me == null) continue; bb = me.DbEntity.SerializeToBytes(); }
                            for (int i = 0; i <= bb.Length - pat.Length; i++)
                            {
                                bool eq = true;
                                for (int k = 0; k < pat.Length; k++) if (bb[i + k] != pat[k]) { eq = false; break; }
                                if (eq) { todo.Add("level|" + nid.Handle + "|" + q0[1] + "|" + q0[2]); break; }
                            }
                        }
                        log.AppendLine("levelAll '" + q0[1] + "': " + todo.Count + " of " + hits.Count);
                    }
                    else if (line.StartsWith("level|")) todo.Add(line);
                    foreach (var lvline in todo)
                    {
                        // level|<handle>|old|new : same-length byte replace (latin1 and utf16) in the serialized object, re-create, erase old
                        var q = lvline.Split('|');
                        ObjectId sid;
                        if (!db.TryGetObjectId(new Handle(Convert.ToInt64(q[1], 16)), out sid)) { log.AppendLine("no " + q[1]); continue; }
                        byte[] b;
                        using (var mc = McObjectManager.GetObject(McObjectId.FromOldIdPtr(sid.OldIdPtr)))
                            b = ((McEntity)mc).DbEntity.SerializeToBytes();
                        int cnt = 0;
                        Func<string, Encoding, byte[]> B = (str, enc0) => str.StartsWith("hex:") ? Enumerable.Range(0, (str.Length - 4) / 2).Select(i => Convert.ToByte(str.Substring(4 + 2 * i, 2), 16)).ToArray() : enc0.GetBytes(str);
                        foreach (var enc in (q[2].StartsWith("hex:") ? new Encoding[] { Encoding.GetEncoding(28591) } : new Encoding[] { Encoding.GetEncoding(28591), Encoding.Unicode }))
                        {
                            var pa = B(q[2], enc); var pr = B(q[3], enc);
                            if (pa.Length != pr.Length) throw new System.Exception("length differs");
                            for (int i = 0; i <= b.Length - pa.Length; i++)
                            {
                                bool eq = true;
                                for (int k = 0; k < pa.Length; k++) if (b[i + k] != pa[k]) { eq = false; break; }
                                if (eq) { Array.Copy(pr, 0, b, i, pr.Length); cnt++; i += pa.Length - 1; }
                            }
                        }
                        if (cnt == 0) { log.AppendLine("level " + q[1] + " pattern not found"); continue; }
                        var ne = McDbEntity.DeserializeNewFromBytes(b);
                        if (ne == null) { log.AppendLine("level " + q[1] + " deserialize null"); continue; }
                        McObjectManager.Add2Document(ne);
                        ne.Update();
                        var nid = new ObjectId(ne.ID.ToOldIdPtr());
                        using (var tr = db.TransactionManager.StartTransaction())
                        {
                            tr.GetObject(sid, OpenMode.ForWrite).Erase();
                            tr.Commit();
                        }
                        log.AppendLine("level " + q[1] + " '" + q[2] + "'->'" + q[3] + "' x" + cnt + " new " + nid.Handle);
                    }
                    if (todo.Count > 0 || line.StartsWith("levelAll|")) continue;
                    var a = line.Trim().Split(' ');
                    if (a.Length < 4 || a[0] != "stretchY") continue;
                    ObjectId id;
                    if (!db.TryGetObjectId(new Handle(Convert.ToInt64(a[1], 16)), out id)) { log.AppendLine("no " + a[1]); continue; }
                    double above = double.Parse(a[2], IC), ynew = double.Parse(a[3], IC);
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForWrite);
                        var pts = new Point3dCollection();
                        e.GetStretchPoints(pts);
                        var sb = new StringBuilder();
                        for (int i = 0; i < pts.Count; i++)
                        {
                            sb.Append(" (" + pts[i].X.ToString("0", IC) + "," + pts[i].Y.ToString("0", IC) + ")");
                            if (pts[i].Y > above)
                            {
                                var idx = new IntegerCollection { i };
                                e.MoveStretchPointsAt(idx, new Vector3d(0, ynew - pts[i].Y, 0));
                            }
                        }
                        log.AppendLine(a[1] + " " + id.ObjectClass.DxfName + " pts" + sb);
                        tr.Commit();
                    }
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                        var x = e.GeometricExtents;
                        log.AppendLine("   now y " + x.MinPoint.Y.ToString("0", IC) + " .. " + x.MaxPoint.Y.ToString("0", IC));
                        tr.Commit();
                    }
                }
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Path.Combine(tmp, "mc4_log.txt"), log.ToString(), Encoding.UTF8);
        }
    }
}
