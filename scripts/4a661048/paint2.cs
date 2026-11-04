using System;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

public class Paint2
{
    const string AREA = "=(0.55*43.3+0.2*50.8+0.594*44.2+0.192*91.9+0.36*32.9+0.19*50.0+0.28*50.2+0.09*50.4+0.09*39.9+0.06*31.8+0.1*42.5+1.11*63.7)";

    static void SetText(Table t, int r, int c, string s, double h, ObjectId ts)
    {
        Cell cell = t.Cells[r, c];
        cell.TextString = s;
        cell.TextStyleId = ts;
        cell.TextHeight = h;
        cell.Alignment = CellAlignment.MiddleCenter;
    }

    static void SetFormula(Table t, int r, int c, string f, string fmt, double h, ObjectId ts)
    {
        Cell cell = t.Cells[r, c];
        cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
        cell.TextString = "";
        if (cell.Contents.Count == 0) cell.Contents.Add();
        cell.Contents[0].Formula = f;
        cell.Contents[0].TextHeight = h;
        cell.TextStyleId = ts;
        cell.DataFormat = fmt;
        cell.Alignment = CellAlignment.MiddleCenter;
    }

    static void SetNum(Table t, int r, int c, double v, string fmt, double h, ObjectId ts)
    {
        Cell cell = t.Cells[r, c];
        cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
        cell.Value = v;
        cell.DataFormat = fmt;
        cell.TextStyleId = ts;
        cell.TextHeight = h;
        cell.Alignment = CellAlignment.MiddleCenter;
    }

    [CommandMethod("PAINTTBL2")]
    public void Run()
    {
        var doc = Application.DocumentManager.MdiActiveDocument;
        var db = doc.Database;
        using (doc.LockDocument())
        using (var tr = db.TransactionManager.StartTransaction())
        {
            try { var old = tr.GetObject(db.GetObjectId(false, new Handle(Convert.ToInt64("6611CC", 16)), 0), OpenMode.ForWrite); if (!old.IsErased) old.Erase(); } catch { }
            long hv = Convert.ToInt64("641368", 16);
            var spec = (Table)tr.GetObject(db.GetObjectId(false, new Handle(hv), 0), OpenMode.ForRead);
            ObjectId ts = spec.Cells[spec.Rows.Count - 1, 0].TextStyleId ?? db.Textstyle;
            double x0 = spec.Position.X;
            double ytop = spec.Position.Y - spec.Height - 150;

            var t = new Table();
            t.SetDatabaseDefaults(db);
            t.TableStyle = spec.TableStyle;
            t.Layer = spec.Layer;
            t.Position = new Point3d(x0, ytop, 0);
            t.SetSize(4, 7);
            double[] w = { 760, 420, 340, 230, 330, 230, 233 };
            for (int c = 0; c < 7; c++) t.Columns[c].Width = w[c];
            double[] rh = { 80, 130, 80, 80 };
            for (int r = 0; r < 4; r++) t.Rows[r].Height = rh[r];
            t.Cells[0, 0].Style = "_TITLE";
            t.Cells[1, 0].Style = "_HEADER";
            for (int c = 0; c < 7; c++) { t.Cells[1, c].Style = "_HEADER"; t.Cells[2, c].Style = "_DATA"; t.Cells[3, c].Style = "_DATA"; }
            t.MergeCells(CellRange.Create(t, 0, 0, 0, 6));

            SetText(t, 0, 0, "Ведомость расхода лакокрасочных материалов", 35, ts);
            string[] hd = { "Наименование материала", "ГОСТ, ТУ", "Площадь окраски, м²", "Кол-во слоев", "Норма расхода на 1 слой, кг/м²", "Коэфф. потерь", "Расход, кг" };
            for (int c = 0; c < 7; c++) SetText(t, 1, c, hd[c], 25, ts);

            SetText(t, 2, 0, "Грунтовка ГФ-021", 25, ts);
            SetText(t, 2, 1, "ГОСТ 25129-2020", 25, ts);
            SetFormula(t, 2, 2, AREA, "%lu2%pr1", 25, ts);
            SetNum(t, 2, 3, 1, "%lu2%pr0", 25, ts);
            SetNum(t, 2, 4, 0.10, "%lu2%pr2", 25, ts);
            SetNum(t, 2, 5, 1.10, "%lu2%pr2", 25, ts);
            SetFormula(t, 2, 6, "=C3*D3*E3*F3", "%lu2%pr1", 25, ts);

            SetText(t, 3, 0, "Эмаль ПФ-115", 25, ts);
            SetText(t, 3, 1, "ГОСТ 6465-76", 25, ts);
            SetFormula(t, 3, 2, "=C3", "%lu2%pr1", 25, ts);
            SetNum(t, 3, 3, 2, "%lu2%pr0", 25, ts);
            SetNum(t, 3, 4, 0.12, "%lu2%pr2", 25, ts);
            SetNum(t, 3, 5, 1.10, "%lu2%pr2", 25, ts);
            SetFormula(t, 3, 6, "=C4*D4*E4*F4", "%lu2%pr1", 25, ts);

            // all grid lines 0.30 mm
            for (int r = 0; r < 4; r++)
                for (int c = 0; c < 7; c++)
                {
                    var b = t.Cells[r, c].Borders;
                    b.Top.LineWeight = LineWeight.LineWeight030; b.Bottom.LineWeight = LineWeight.LineWeight030;
                    b.Left.LineWeight = LineWeight.LineWeight030; b.Right.LineWeight = LineWeight.LineWeight030;
                }

            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
            ms.AppendEntity(t);
            tr.AddNewlyCreatedDBObject(t, true);
            t.GenerateLayout();
            tr.Commit();
            doc.Editor.WriteMessage("\nPAINT table " + t.Handle + " at " + t.Position + " h=" + t.Height + "\n");
        }
        db.EvaluateFields();
    }
}
