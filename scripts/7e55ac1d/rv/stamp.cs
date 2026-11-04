using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RB
{
    public class LoadOpts : IFamilyLoadOptions
    {
        public bool OnFamilyFound(bool familyInUse, out bool overwriteParameterValues) { overwriteParameterValues = true; return true; }
        public bool OnSharedFamilyFound(Family sharedFamily, bool familyInUse, out FamilySource source, out bool overwriteParameterValues)
        { source = FamilySource.Family; overwriteParameterValues = true; return true; }
    }

    public partial class App
    {
        // КЖ titleblock «(основная_надпись)» → КМ stamp of RAS Group Project: company, logo, roles and names as in the DWG album
        static void FixStamp(Document doc, string logo)
        {
            Family fam = Find<Family>(doc, f => f.Name == "(основная_надпись)");
            Document fd = doc.EditFamily(fam);
            foreach (Family nf in new FilteredElementCollector(fd).OfClass(typeof(Family)).Cast<Family>().Where(f => f.Name.StartsWith("RAS_Фамилия")).ToList())
            {
                Document nd = fd.EditFamily(nf);
                using (Transaction t = new Transaction(nd, "no lookup"))
                {
                    t.Start();
                    FamilyParameter pe = nd.FamilyManager.get_Parameter("Ошибка в фамилии");
                    if (pe != null) nd.FamilyManager.SetFormula(pe, "1 = 0");
                    t.Commit();
                }
                nd.LoadFamily(fd, new LoadOpts());
                nd.Close(false);
                L("  stamp: surname check off in " + nf.Name);
            }
            Dictionary<string, string> names = new Dictionary<string, string> { { "ГИП", "Казангапов А" }, { "ГАП", "Хасанова К" }, { "Разработал", "Ауез Б" }, { "Н.Контроль", "Приколотов" } };
            Dictionary<string, string> assocVal = new Dictionary<string, string>();
            using (Transaction t = new Transaction(fd, "stamp"))
            {
                t.Start();
                List<TextNote> notes = new FilteredElementCollector(fd).OfClass(typeof(TextNote)).Cast<TextNote>().ToList();
                TextNote vsn = null;
                foreach (TextNote n in notes)
                {
                    string s = n.Text.Trim();
                    if (s == "ТОО \"VSN\"") { n.Text = "ТОО \"RAS Group Project\""; vsn = n; }
                    else if (s == "Глав.спец") n.Text = "ГИП";
                    else if (s == "Проверил") n.Text = "ГАП";
                }
                foreach (TextNote n in notes.Where(n => n.IsValidObject && (n.Text.Trim() == "ГРП" || n.Text.Trim() == "Бекмагамбетов А." || n.Text.Trim() == "09.2025")).ToList()) fd.Delete(n.Id);
                List<TextNote> labels = new FilteredElementCollector(fd).OfClass(typeof(TextNote)).Cast<TextNote>().Where(n => names.ContainsKey(n.Text.Trim())).ToList();
                foreach (FamilyInstance fi in new FilteredElementCollector(fd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Symbol.FamilyName.StartsWith("RAS_Фамилия")))
                {
                    XYZ p = ((LocationPoint)fi.Location).Point;
                    TextNote best = null; double bd = 1e9;
                    foreach (TextNote lb in labels)
                    {
                        double dx = p.X - lb.Coord.X, dy = Math.Abs(p.Y - lb.Coord.Y);
                        if (dx > 0 && dx < 60 * MM && dy < 4 * MM && dy < bd) { bd = dy; best = lb; }
                    }
                    Parameter fp = fi.LookupParameter("Фамилия");
                    FamilyParameter ap = fp != null ? fd.FamilyManager.GetAssociatedFamilyParameter(fp) : null;
                    L("  stamp row at " + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + " label " + (best != null ? best.Text.Trim() : "-") + " param " + (ap != null ? ap.Definition.Name : "-"));
                    if (best == null || ap == null) continue;
                    assocVal[ap.Definition.Name] = names[best.Text.Trim()];
                    foreach (FamilyType ft in fd.FamilyManager.Types) { fd.FamilyManager.CurrentType = ft; fd.FamilyManager.Set(ap, names[best.Text.Trim()]); }
                }
                if (vsn != null && File.Exists(logo))
                {
                    ImageInstance near = null; double nd2 = 1e9;
                    foreach (ImageInstance ii in new FilteredElementCollector(fd).OfClass(typeof(ImageInstance)).Cast<ImageInstance>())
                    {
                        double dd = ii.GetLocation(BoxPlacement.Center).DistanceTo(vsn.Coord);
                        if (dd < nd2) { nd2 = dd; near = ii; }
                    }
                    if (near != null)
                    {
                        ImageType it = (ImageType)fd.GetElement(near.GetTypeId());
                        it.ReloadFrom(new ImageTypeOptions(logo, false, ImageTypeSource.Import));
                        L("  stamp logo replaced (" + it.Name + ", " + Math.Round(nd2 / MM) + " mm from the company text)");
                    }
                }
                t.Commit();
            }
            fd.LoadFamily(doc, new LoadOpts());
            fd.Close(false);
            Tx(doc, "stamp names", delegate
            {
                foreach (FamilyInstance tbi in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().Cast<FamilyInstance>())
                {
                    foreach (KeyValuePair<string, string> kv in assocVal)
                    {
                        Parameter p = tbi.LookupParameter(kv.Key) ?? tbi.Symbol.LookupParameter(kv.Key);
                        if (p != null && !p.IsReadOnly) p.Set(kv.Value);
                    }
                    Parameter g = tbi.LookupParameter("Фамилия ГИП");
                    if (g != null && !g.IsReadOnly) g.Set("Казангапов А");
                }
            });
        }
    }
}
