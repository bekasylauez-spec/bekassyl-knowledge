using System;
using System.IO;
using System.Text;
using System.Reflection;
using System.ComponentModel;
using System.Collections;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Multicad;

[assembly: CommandClass(typeof(BkLvl.Cmds))]
namespace BkLvl
{
    public class Cmds
    {
        static string Dir = @"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\4c62aff2-a55a-4637-9af2-523dd75c9ccb\scratchpad\";
        static StringBuilder log = new StringBuilder();
        static void L(string s) { log.AppendLine(s); }

        static object GetProp(object o, string name)
        {
            if (o == null) return null;
            var p = o.GetType().GetProperty(name, BindingFlags.Public | BindingFlags.Instance);
            return p == null ? null : p.GetValue(o, null);
        }

        static void SetText(ObjectId id, string nt)
        {
            McObjectId mid = McObjectId.FromOldIdPtr(id.OldIdPtr);
            using (McObject mo = mid.GetObject())
            {
                object props = GetProp(GetProp(mo, "DbObject"), "ObjectProperties");
                PropertyDescriptorCollection pdc = (props is ICustomTypeDescriptor) ? ((ICustomTypeDescriptor)props).GetProperties() : TypeDescriptor.GetProperties(props);
                foreach (PropertyDescriptor pd in pdc)
                    if (pd.Name == "Text") { pd.SetValue(props, nt); L("  text " + pd.GetValue(props)); return; }
            }
        }

        // lvl_copy.txt lines: srcHandle;tipX;tipY;text  -> clone level mark so that its tip grip lands on (x,y)
        [CommandMethod("LVLCOPY")]
        public void LvlCopy()
        {
            log.Clear();
            Database db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                foreach (string line in File.ReadAllLines(Dir + "lvl_copy.txt", Encoding.UTF8))
                {
                    if (line.Trim().Length == 0) continue;
                    string[] f = line.Split(';');
                    ObjectId src; db.TryGetObjectId(new Handle(Convert.ToInt64(f[0].Trim(), 16)), out src);
                    double x = double.Parse(f[1], System.Globalization.CultureInfo.InvariantCulture);
                    double y = double.Parse(f[2], System.Globalization.CultureInfo.InvariantCulture);
                    ObjectId nid;
                    using (Transaction tr = db.TransactionManager.StartTransaction())
                    {
                        Entity se = (Entity)tr.GetObject(src, OpenMode.ForRead);
                        ObjectIdCollection ids = new ObjectIdCollection(); ids.Add(src);
                        IdMapping map = new IdMapping();
                        db.DeepCloneObjects(ids, se.OwnerId, map, false);
                        nid = map[src].Value;
                        Entity ne = (Entity)tr.GetObject(nid, OpenMode.ForWrite);
                        Point3dCollection gp = new Point3dCollection(); IntegerCollection a = new IntegerCollection(), b = new IntegerCollection();
                        ne.GetGripPoints(gp, a, b);
                        Point3d tip = gp[0];
                        foreach (Point3d p in gp) if (p.Y < tip.Y - 1e-6) tip = p;
                        ne.TransformBy(Matrix3d.Displacement(new Point3d(x, y, 0) - tip));
                        tr.Commit();
                    }
                    SetText(nid, f[3]);
                    L("copied " + f[3] + " -> " + nid.Handle);
                }
            }
            catch (System.Exception e) { L("ERR " + e); }
            File.WriteAllText(Dir + "lvl_log.txt", log.ToString(), Encoding.UTF8);
        }

        // job file lines: handle;newText   (newText empty = only dump)
        [CommandMethod("LVLSET")]
        public void LvlSet()
        {
            log.Clear();
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            try
            {
                string[] lines = File.ReadAllLines(Dir + "lvl_job.txt", Encoding.UTF8);
                foreach (string line in lines)
                {
                    if (line.Trim().Length == 0) continue;
                    string[] f = line.Split(';');
                    string h = f[0].Trim(); string nt = f.Length > 1 ? f[1] : "";
                    ObjectId id;
                    if (!db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) { L("nohandle " + h); continue; }
                    using (Transaction tr = db.TransactionManager.StartTransaction())
                    {
                        Entity ent = (Entity)tr.GetObject(id, OpenMode.ForRead);
                        Extents3d ex = ent.GeometricExtents;
                        L("H " + h + " " + ent.GetType().Name + " ext " + ex.MinPoint + " " + ex.MaxPoint);
                        Point3dCollection gp = new Point3dCollection(); IntegerCollection a = new IntegerCollection(), b = new IntegerCollection();
                        try { ent.GetGripPoints(gp, a, b); foreach (Point3d p in gp) L("  grip " + p); } catch (System.Exception e) { L("  grip err " + e.Message); }
                        tr.Commit();
                    }
                    McObjectId mid = McObjectId.FromOldIdPtr(id.OldIdPtr);
                    using (McObject mo = mid.GetObject())
                    {
                        L("  mc " + (mo == null ? "null" : mo.GetType().FullName));
                        object dbo = GetProp(mo, "DbObject") ?? GetProp(mo, "DbEntity");
                        L("  dbo " + (dbo == null ? "null" : dbo.GetType().FullName));
                        object props = GetProp(dbo, "ObjectProperties");
                        L("  props " + (props == null ? "null" : props.GetType().FullName));
                        PropertyDescriptorCollection pdc = null;
                        if (props is ICustomTypeDescriptor) pdc = ((ICustomTypeDescriptor)props).GetProperties();
                        else if (props != null) pdc = TypeDescriptor.GetProperties(props);
                        if (pdc != null)
                        {
                            foreach (PropertyDescriptor pd in pdc)
                            {
                                object v = null; try { v = pd.GetValue(props); } catch { }
                                L("    " + pd.Name + " [" + pd.DisplayName + "] = " + v + " ro=" + pd.IsReadOnly);
                            }
                            if (nt.Length > 0)
                            {
                                bool done = false;
                                foreach (PropertyDescriptor pd in pdc)
                                {
                                    if (pd.Name == "Text" || pd.DisplayName == "Text")
                                    {
                                        object cur = pd.GetValue(props);
                                        if (cur is string)
                                        {
                                            using (Transaction tr2 = db.TransactionManager.StartTransaction())
                                            {
                                                tr2.GetObject(id, OpenMode.ForWrite);
                                                pd.SetValue(props, nt);
                                                tr2.Commit();
                                            }
                                            L("  SET " + cur + " -> " + nt + " now=" + pd.GetValue(props)); done = true; break;
                                        }
                                    }
                                }
                                if (!done) L("  SET failed: no string Text");
                            }
                        }
                        
                    }
                }
            }
            catch (System.Exception e) { L("ERR " + e); }
            File.WriteAllText(Dir + "lvl_log.txt", log.ToString(), Encoding.UTF8);
        }
    }
}
