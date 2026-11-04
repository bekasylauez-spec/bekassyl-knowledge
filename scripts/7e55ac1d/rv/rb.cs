using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Events;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    public class NoWarn : IFailuresPreprocessor
    {
        public FailureProcessingResult PreprocessFailures(FailuresAccessor fa)
        {
            foreach (FailureMessageAccessor f in fa.GetFailureMessages())
            {
                if (f.GetSeverity() == FailureSeverity.Warning) fa.DeleteWarning(f);
                else { try { fa.ResolveFailure(f); } catch { } }
            }
            return FailureProcessingResult.Continue;
        }
    }

    public partial class App : IExternalApplication
    {
        static string JobDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "rvjob");
        static StringBuilder Log = new StringBuilder();
        bool busy = false;
        static bool inJob = false;
        const double MM = 1.0 / 304.8;

        public Result OnStartup(UIControlledApplication a)
        {
            a.Idling += OnIdling;
            a.DialogBoxShowing += OnDialog;
            a.ControlledApplication.ApplicationInitialized += OnInit;
            Trace("startup " + JobDir);
            return Result.Succeeded;
        }
        public Result OnShutdown(UIControlledApplication a) { return Result.Succeeded; }

        static void L(string s) { Log.AppendLine(DateTime.Now.ToString("HH:mm:ss ") + s); }

        void OnDialog(object sender, DialogBoxShowingEventArgs e)
        {
            if (!inJob) return;
            L("dialog " + e.DialogId);
            try { e.OverrideResult(1); } catch { }
        }

        static int idleCount = 0;
        static void Trace(string s) { try { Directory.CreateDirectory(JobDir); File.AppendAllText(Path.Combine(JobDir, "trace.txt"), DateTime.Now.ToString("HH:mm:ss ") + s + Environment.NewLine); } catch { } }

        void OnInit(object sender, ApplicationInitializedEventArgs e)
        {
            Trace("init");
            Application app = sender as Application;
            RunJob(app, new UIApplication(app));
        }

        void OnIdling(object sender, IdlingEventArgs e)
        {
            if (idleCount++ < 3) Trace("idle " + File.Exists(Path.Combine(JobDir, "job.txt")));
            RunJob(((UIApplication)sender).Application, (UIApplication)sender);
        }

        void RunJob(Application dbapp, UIApplication uiapp)
        {
            if (busy) return;
            string job = Path.Combine(JobDir, "job.txt");
            if (!File.Exists(job)) return;
            busy = true; inJob = true;
            Dictionary<string, string> J = new Dictionary<string, string>();
            string outPath = null;
            try
            {
                foreach (string ln in File.ReadAllLines(job, Encoding.UTF8))
                {
                    int i = ln.IndexOf('=');
                    if (i > 0) J[ln.Substring(0, i).Trim()] = ln.Substring(i + 1).Trim();
                }
                File.Delete(job);
                if (J.ContainsKey("mode") && J["mode"] == "dump")
                {
                    foreach (string k in J.Keys.Where(x => x.StartsWith("src")).ToList())
                    {
                        L("dump " + J[k]);
                        try { Dumper.Dump(dbapp, J[k], Path.Combine(JobDir, "dump_" + k + ".txt")); L("dump ok"); }
                        catch (Exception ex) { L("dump fail " + ex.Message); }
                    }
                }
                else if (J.ContainsKey("mode") && J["mode"] == "famdump") FamDumper.Dump(dbapp, J["src"], J["fam"], Path.Combine(JobDir, "famdump.txt"));
                else if (J.ContainsKey("mode") && J["mode"] == "rfadump") RfaDumper.Dump(dbapp, J["files"].Split(';'), Path.Combine(JobDir, "rfadump.txt"));
                else if (J.ContainsKey("mode") && J["mode"] == "secdump") SecDumper.Dump(dbapp, J["template"], Path.Combine(JobDir, "secdump.txt"));
                else if (J.ContainsKey("mode") && J["mode"] == "km2") outPath = BuildKM2(dbapp, J);
                else if (J.ContainsKey("mode") && J["mode"] == "fix") outPath = FixInPlace(dbapp, J);
                else if (J.ContainsKey("mode") && J["mode"] == "km") outPath = BuildKM(dbapp, J);
                else outPath = Build(dbapp, J);
            }
            catch (Exception ex) { L("ERROR " + ex.ToString()); }
            inJob = false;
            File.WriteAllText(Path.Combine(JobDir, "done.txt"), Log.ToString(), Encoding.UTF8);
            if (outPath != null && J.ContainsKey("open") && J["open"] == "1")
            {
                try { uiapp.OpenAndActivateDocument(outPath); }
                catch (Exception ex) { L("open failed " + ex.Message); File.WriteAllText(Path.Combine(JobDir, "done.txt"), Log.ToString(), Encoding.UTF8); }
            }
            busy = false;
        }

        static void Tx(Document d, string name, Action act)
        {
            using (Transaction t = new Transaction(d, name))
            {
                t.Start();
                FailureHandlingOptions o = t.GetFailureHandlingOptions();
                o.SetFailuresPreprocessor(new NoWarn());
                t.SetFailureHandlingOptions(o);
                act();
                t.Commit();
            }
        }

        static CurveArray Rect(Func<double, double, XYZ> P, double a, double b)
        {
            XYZ p1 = P(-a / 2, -b / 2), p2 = P(a / 2, -b / 2), p3 = P(a / 2, b / 2), p4 = P(-a / 2, b / 2);
            CurveArray c = new CurveArray();
            c.Append(Line.CreateBound(p1, p2)); c.Append(Line.CreateBound(p2, p3));
            c.Append(Line.CreateBound(p3, p4)); c.Append(Line.CreateBound(p4, p1));
            return c;
        }

        static List<PlanarFace> Faces(Element el)
        {
            Options op = new Options(); op.ComputeReferences = true;
            List<PlanarFace> r = new List<PlanarFace>();
            foreach (GeometryObject g in el.get_Geometry(op))
            {
                Solid s = g as Solid;
                if (s == null) continue;
                foreach (Face f in s.Faces) { PlanarFace pf = f as PlanarFace; if (pf != null) r.Add(pf); }
            }
            return r;
        }

        static void SteelMaterial(Document fd, Extrusion ex)
        {
            try
            {
                Parameter mt = fd.OwnerFamily.get_Parameter(BuiltInParameter.FAMILY_STRUCT_MATERIAL_TYPE);
                if (mt != null && !mt.IsReadOnly) mt.Set((int)StructuralMaterialType.Steel);
            }
            catch (Exception e) { L("  mattype " + e.Message); }
            try
            {
                Material m = new FilteredElementCollector(fd).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(x => x.Name == "Сталь С245");
                if (m == null) { m = (Material)fd.GetElement(Material.Create(fd, "Сталь С245")); m.Color = new Color(150, 155, 165); m.MaterialClass = "Металл"; }
                ex.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM).Set(m.Id);
            }
            catch (Exception e) { L("  mat " + e.Message); }
        }

        static void SetType(Document fd, string name)
        {
            FamilyManager fm = fd.FamilyManager;
            if (fm.CurrentType == null) fm.NewType(name);
            else fm.RenameCurrentType(name);
        }

        // framing family: hollow rectangular tube b (horizontal) x h (vertical) x t, length locked to the end reference planes
        static string MakeBeamFamily(Application app, string rft, string dir, string name, double b, double h, double t)
        {
            Document fd = app.NewFamilyDocument(rft);
            Tx(fd, "tube", delegate
            {
                List<Extrusion> old = new FilteredElementCollector(fd).OfClass(typeof(Extrusion)).Cast<Extrusion>().ToList();
                BoundingBoxXYZ bb = old[0].get_BoundingBox(null);
                double x0 = bb.Min.X, x1 = bb.Max.X;
                List<ReferencePlane> rps = new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().ToList();
                ReferencePlane rp0 = null, rp1 = null;
                foreach (ReferencePlane rp in rps)
                {
                    if (Math.Abs(Math.Abs(rp.Normal.X) - 1) > 1e-6) continue;
                    if (Math.Abs(rp.BubbleEnd.X - x0) < 1e-4) rp0 = rp;
                    if (Math.Abs(rp.BubbleEnd.X - x1) < 1e-4) rp1 = rp;
                }
                L("  beam tpl x0=" + (x0 / MM).ToString("0") + " x1=" + (x1 / MM).ToString("0") + " rp0=" + (rp0 != null ? rp0.Name : "-") + " rp1=" + (rp1 != null ? rp1.Name : "-") + " zc=" + ((bb.Min.Z + bb.Max.Z) / 2 / MM).ToString("0"));
                foreach (Extrusion e in old) fd.Delete(e.Id);
                SketchPlane sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisX, new XYZ(x0, 0, 0)));
                CurveArrArray prof = new CurveArrArray();
                prof.Append(Rect(delegate(double u, double v) { return new XYZ(x0, u, v); }, b * MM, h * MM));
                prof.Append(Rect(delegate(double u, double v) { return new XYZ(x0, u, v); }, (b - 2 * t) * MM, (h - 2 * t) * MM));
                Extrusion ex = fd.FamilyCreate.NewExtrusion(true, prof, sp, x1 - x0);
                fd.Regenerate();
                View pv = new FilteredElementCollector(fd).OfClass(typeof(ViewPlan)).Cast<View>().First(v => !v.IsTemplate);
                foreach (PlanarFace f in Faces(ex))
                {
                    if (Math.Abs(Math.Abs(f.FaceNormal.X) - 1) > 1e-6) continue;
                    ReferencePlane rp = Math.Abs(f.Origin.X - x0) < 1e-4 ? rp0 : (Math.Abs(f.Origin.X - x1) < 1e-4 ? rp1 : null);
                    if (rp == null) continue;
                    Dimension al = fd.FamilyCreate.NewAlignment(pv, rp.GetReference(), f.Reference);
                    al.IsLocked = true;
                }
                SteelMaterial(fd, ex);
                SetType(fd, name);
            });
            string p = Path.Combine(dir, name + ".rfa");
            SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true;
            fd.SaveAs(p, so); fd.Close(false);
            return p;
        }

        // column family: hollow tube b (along X) x h (along Y) x t between the lower and upper reference levels
        static string MakeColumnFamily(Application app, string rft, string dir, string name, double b, double h, double t)
        {
            Document fd = app.NewFamilyDocument(rft);
            Tx(fd, "col", delegate
            {
                List<Level> lv = new FilteredElementCollector(fd).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation).ToList();
                Level lo = lv[0], hi = lv[lv.Count - 1];
                L("  col tpl levels " + lo.Name + " " + (lo.Elevation / MM).ToString("0") + " / " + hi.Name + " " + (hi.Elevation / MM).ToString("0"));
                foreach (Extrusion e in new FilteredElementCollector(fd).OfClass(typeof(Extrusion)).Cast<Extrusion>().ToList()) fd.Delete(e.Id);
                SketchPlane sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, new XYZ(0, 0, lo.Elevation)));
                CurveArrArray prof = new CurveArrArray();
                prof.Append(Rect(delegate(double u, double v) { return new XYZ(u, v, lo.Elevation); }, b * MM, h * MM));
                prof.Append(Rect(delegate(double u, double v) { return new XYZ(u, v, lo.Elevation); }, (b - 2 * t) * MM, (h - 2 * t) * MM));
                Extrusion ex = fd.FamilyCreate.NewExtrusion(true, prof, sp, hi.Elevation - lo.Elevation);
                fd.Regenerate();
                View ev = new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(v => !v.IsTemplate && v.ViewType == ViewType.Elevation && Math.Abs(v.ViewDirection.Y) > 0.9);
                foreach (PlanarFace f in Faces(ex))
                {
                    if (Math.Abs(Math.Abs(f.FaceNormal.Z) - 1) > 1e-6) continue;
                    Level l = Math.Abs(f.Origin.Z - lo.Elevation) < 1e-4 ? lo : (Math.Abs(f.Origin.Z - hi.Elevation) < 1e-4 ? hi : null);
                    if (l == null) continue;
                    Dimension al = fd.FamilyCreate.NewAlignment(ev, l.GetPlaneReference(), f.Reference);
                    al.IsLocked = true;
                }
                SteelMaterial(fd, ex);
                SetType(fd, name);
            });
            string p = Path.Combine(dir, name + ".rfa");
            SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true;
            fd.SaveAs(p, so); fd.Close(false);
            return p;
        }

        static FamilySymbol LoadSym(Document d, string path)
        {
            Family fam;
            d.LoadFamily(path, out fam);
            if (fam == null)
            {
                string n = Path.GetFileNameWithoutExtension(path);
                fam = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().First(f => f.Name == n);
            }
            FamilySymbol s = (FamilySymbol)d.GetElement(fam.GetFamilySymbolIds().First());
            if (!s.IsActive) s.Activate();
            return s;
        }

        static double D(string s) { return double.Parse(s, System.Globalization.CultureInfo.InvariantCulture); }

        static void SetP(Element e, BuiltInParameter bip, string v)
        {
            Parameter p = e.get_Parameter(bip);
            if (p != null && !p.IsReadOnly) p.Set(v);
        }

        static string Build(Application app, Dictionary<string, string> J)
        {
            string famDir = J["famdir"];
            Directory.CreateDirectory(famDir);
            List<string[]> rows = File.ReadAllLines(J["model"], Encoding.UTF8).Where(x => x.Trim().Length > 0).Select(x => x.Split('|')).ToList();
            L("rows " + rows.Count);

            // families
            Dictionary<string, string> beamRfa = new Dictionary<string, string>(), colRfa = new Dictionary<string, string>();
            HashSet<string> colFams = new HashSet<string>(rows.Where(r => r[0] == "C").Select(r => r[1]));
            HashSet<string> beamFams = new HashSet<string>(rows.Where(r => r[0] == "B").Select(r => r[1]));
            foreach (string[] r in rows.Where(r => r[0] == "F"))
            {
                double b = D(r[2]), h = D(r[3]), t = D(r[4]);
                if (beamFams.Contains(r[1])) { beamRfa[r[1]] = MakeBeamFamily(app, J["rftbeam"], famDir, r[1], b, b == h ? h : h, t); L("family beam " + r[1]); }
                if (colFams.Contains(r[1])) { colRfa[r[1]] = MakeColumnFamily(app, J["rftcol"], famDir, r[1] + " (стойка)", b, h, t); L("family col " + r[1]); }
            }

            Document doc = app.NewProjectDocument(J["template"]);
            Level lvBase = null, lvTop = null;
            Dictionary<string, FamilySymbol> bs = new Dictionary<string, FamilySymbol>(), cs = new Dictionary<string, FamilySymbol>();
            Tx(doc, "setup", delegate
            {
                foreach (KeyValuePair<string, string> kv in beamRfa) bs[kv.Key] = LoadSym(doc, kv.Value);
                foreach (KeyValuePair<string, string> kv in colRfa) cs[kv.Key] = LoadSym(doc, kv.Value);

                Material steel = new FilteredElementCollector(doc).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(m => m.Name == "Сталь С245");
                if (steel == null) { steel = (Material)doc.GetElement(Material.Create(doc, "Сталь С245")); }
                L("steel material " + steel.Name);
                foreach (FamilySymbol s in bs.Values.Concat(cs.Values))
                {
                    Parameter p = s.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM);
                    if (p != null && !p.IsReadOnly) p.Set(steel.Id);
                }

                List<Level> lv = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation).ToList();
                L("template levels: " + string.Join(", ", lv.Select(x => x.Name + "@" + (x.Elevation / MM).ToString("0"))));
                Level l0 = lv[0];
                l0.Elevation = 0; l0.Name = "±0,000";
                lvBase = lv.Count > 1 ? lv[1] : Level.Create(doc, 870 * MM);
                lvBase.Elevation = 870 * MM; lvBase.Name = "Низ стоек +0,870";
                lvTop = lv.Count > 2 ? lv[2] : Level.Create(doc, 4620 * MM);
                lvTop.Elevation = 4620 * MM; lvTop.Name = "Верх покрытия +4,620";
                for (int i = 3; i < lv.Count; i++) doc.Delete(lv[i].Id);

                ViewFamilyType pvt = new FilteredElementCollector(doc).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>()
                    .FirstOrDefault(v => v.ViewFamily == ViewFamily.StructuralPlan) ??
                    new FilteredElementCollector(doc).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(v => v.ViewFamily == ViewFamily.FloorPlan);
                HashSet<ElementId> withPlan = new HashSet<ElementId>(new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<ViewPlan>()
                    .Where(v => !v.IsTemplate && v.GenLevel != null).Select(v => v.GenLevel.Id));
                foreach (Level l in new Level[] { lvBase, lvTop })
                    if (!withPlan.Contains(l.Id)) { ViewPlan vp = ViewPlan.Create(doc, pvt.Id, l.Id); try { vp.Name = l.Name; } catch { } }

                foreach (string[] r in rows.Where(r => r[0] == "G"))
                {
                    Grid g = Grid.Create(doc, Line.CreateBound(new XYZ(D(r[2]) * MM, D(r[3]) * MM, 0), new XYZ(D(r[4]) * MM, D(r[5]) * MM, 0)));
                    g.Name = r[1];
                }
            });
            L("setup done");

            int nb = 0, nc = 0, nerr = 0;
            Tx(doc, "frame", delegate
            {
                foreach (string[] r in rows.Where(r => r[0] == "C"))
                {
                    FamilySymbol s = cs[r[1]];
                    double x = D(r[3]) * MM, y = D(r[4]) * MM, z1 = D(r[5]) * MM, z2 = D(r[6]) * MM;
                    FamilyInstance fi = doc.Create.NewFamilyInstance(new XYZ(x, y, z1), s, lvBase, StructuralType.Column);
                    fi.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).Set(z1 - lvBase.Elevation);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvTop.Id);
                    fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(z2 - lvTop.Elevation);
                    SetP(fi, BuiltInParameter.ALL_MODEL_MARK, r[2]);
                    SetP(fi, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, "ЛИРА КЭ " + r[7]);
                    nc++;
                }
                foreach (string[] r in rows.Where(r => r[0] == "B"))
                {
                    try
                    {
                        FamilySymbol s = bs[r[1]];
                        XYZ a = new XYZ(D(r[3]) * MM, D(r[4]) * MM, D(r[5]) * MM), b = new XYZ(D(r[6]) * MM, D(r[7]) * MM, D(r[8]) * MM);
                        string mk = r[2];
                        bool brace = mk == "Р1" || mk == "СГ1" || mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "Пк1";
                        FamilyInstance fi = doc.Create.NewFamilyInstance(Line.CreateBound(a, b), s, lvBase, brace ? StructuralType.Brace : StructuralType.Beam);
                        StructuralFramingUtils.DisallowJoinAtEnd(fi, 0);
                        StructuralFramingUtils.DisallowJoinAtEnd(fi, 1);
                        Parameter zj = fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION);
                        if (r[9] == "B")
                        {
                            if (zj != null) zj.Set((int)ZJustification.Bottom);
                            fi.get_Parameter(BuiltInParameter.Z_OFFSET_VALUE).Set(40 * MM);
                        }
                        else if (zj != null) zj.Set((int)ZJustification.Center);
                        SetP(fi, BuiltInParameter.ALL_MODEL_MARK, mk);
                        SetP(fi, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, "ЛИРА КЭ " + r[10]);
                        nb++;
                    }
                    catch (Exception ex) { nerr++; if (nerr < 10) L("beam err " + string.Join("|", r) + " : " + ex.Message); }
                }
            });
            L("columns " + nc + " framing " + nb + " errors " + nerr);

            Tx(doc, "plates", delegate
            {
                foreach (string[] r in rows.Where(r => r[0] == "D"))
                {
                    double x = D(r[2]) * MM, y = D(r[3]) * MM, z = D(r[4]) * MM, a = D(r[5]) * MM, b = D(r[6]) * MM, t = D(r[7]) * MM;
                    CurveLoop cl = new CurveLoop();
                    XYZ p1 = new XYZ(x - a / 2, y - b / 2, z - t), p2 = new XYZ(x + a / 2, y - b / 2, z - t), p3 = new XYZ(x + a / 2, y + b / 2, z - t), p4 = new XYZ(x - a / 2, y + b / 2, z - t);
                    cl.Append(Line.CreateBound(p1, p2)); cl.Append(Line.CreateBound(p2, p3)); cl.Append(Line.CreateBound(p3, p4)); cl.Append(Line.CreateBound(p4, p1));
                    Solid so = GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { cl }, XYZ.BasisZ, t);
                    DirectShape ds = DirectShape.CreateElement(doc, new ElementId(BuiltInCategory.OST_GenericModel));
                    ds.SetShape(new List<GeometryObject> { so });
                    try { ds.SetName(r[1]); } catch { }
                    SetP(ds, BuiltInParameter.ALL_MODEL_MARK, r[1]);
                    SetP(ds, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, "Закладная деталь (раздел КЖ)");
                }
            });

            Tx(doc, "views", delegate
            {
                ViewFamilyType t3 = new FilteredElementCollector(doc).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(v => v.ViewFamily == ViewFamily.ThreeDimensional);
                View3D v3 = View3D.CreateIsometric(doc, t3.Id);
                try { v3.Name = "3D Навес 1 над рампой"; } catch { }
                v3.DetailLevel = ViewDetailLevel.Fine;
                v3.DisplayStyle = DisplayStyle.ShadingWithEdges;
                XYZ f0 = new XYZ(1, 1, -0.7).Normalize();
                v3.SetOrientation(new ViewOrientation3D(new XYZ(-40, -30, 25), f0.CrossProduct(XYZ.BasisZ).CrossProduct(f0).Normalize(), f0));
                ProjectInfo pi = doc.ProjectInformation;
                try
                {
                    pi.Name = "Навес 1 над рампой паркинга";
                    pi.Number = "3669-1-КМ";
                    pi.Address = J.ContainsKey("address") ? J["address"] : "";
                }
                catch { }
            });

            try
            {
                View3D v3e = new FilteredElementCollector(doc).OfClass(typeof(View3D)).Cast<View3D>().First(v => v.Name == "3D Навес 1 над рампой");
                foreach (string side in new string[] { "a", "b" })
                {
                    if (side == "b")
                    {
                        Tx(doc, "orient", delegate
                        {
                            XYZ f = new XYZ(-1, -1, -0.7).Normalize();
                            v3e.SetOrientation(new ViewOrientation3D(new XYZ(80, 40, 25), f.CrossProduct(XYZ.BasisZ).CrossProduct(f).Normalize(), f));
                        });
                    }
                    ImageExportOptions io = new ImageExportOptions();
                    io.ExportRange = ExportRange.SetOfViews;
                    io.SetViewsAndSheets(new List<ElementId> { v3e.Id });
                    io.FilePath = Path.Combine(JobDir, "view_" + side);
                    io.ZoomType = ZoomFitType.FitToPage;
                    io.PixelSize = 2400;
                    io.HLRandWFViewsFileType = ImageFileType.PNG;
                    io.ShadowViewsFileType = ImageFileType.PNG;
                    io.ImageResolution = ImageResolution.DPI_150;
                    doc.ExportImage(io);
                }
                Tx(doc, "orient back", delegate
                {
                    XYZ f = new XYZ(1, 1, -0.7).Normalize();
                    v3e.SetOrientation(new ViewOrientation3D(new XYZ(-40, -30, 25), f.CrossProduct(XYZ.BasisZ).CrossProduct(f).Normalize(), f));
                });
            }
            catch (Exception ex) { L("image " + ex.Message); }

            string outPath = J["out"];
            SaveAsOptions sao = new SaveAsOptions(); sao.OverwriteExistingFile = true;
            doc.SaveAs(outPath, sao);
            doc.Close(false);
            L("saved " + outPath);
            return outPath;
        }
    }
}
