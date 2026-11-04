using System;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;

public class PaintK
{
    static void Num(Table t, int r, int c, double v, string fmt, ObjectId ts)
    {
        Cell cell = t.Cells[r, c];
        cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
        cell.Value = v;
        cell.DataFormat = fmt;
        cell.TextStyleId = ts;
        cell.TextHeight = 25;
        cell.Alignment = CellAlignment.MiddleCenter;
    }

    static void Formula(Table t, int r, int c, string f, ObjectId ts)
    {
        Cell cell = t.Cells[r, c];
        cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
        cell.TextString = "";
        if (cell.Contents.Count == 0) cell.Contents.Add();
        cell.Contents[0].Formula = f;
        cell.Contents[0].TextHeight = 25;
        cell.TextStyleId = ts;
        cell.DataFormat = "%lu2%pr1";
        cell.Alignment = CellAlignment.MiddleCenter;
    }

    [CommandMethod("PAINTK")]
    public void Run()
    {
        var doc = Application.DocumentManager.MdiActiveDocument;
        var db = doc.Database;
        using (doc.LockDocument())
        using (var tr = db.TransactionManager.StartTransaction())
        {
            var t = (Table)tr.GetObject(db.GetObjectId(false, new Handle(Convert.ToInt64("6611CC", 16)), 0), OpenMode.ForWrite);
            if (t.Columns.Count != 6) { doc.Editor.WriteMessage("\nPAINTK: already " + t.Columns.Count + " cols\n"); return; }
            ObjectId ts = t.Cells[1, 0].TextStyleId ?? db.Textstyle;
            t.UnmergeCells(CellRange.Create(t, 0, 0, 0, 5));
            t.InsertColumns(5, 230, 1);
            double[] w = { 760, 420, 340, 230, 330, 230, 233 };
            for (int c = 0; c < 7; c++) t.Columns[c].Width = w[c];
            t.MergeCells(CellRange.Create(t, 0, 0, 0, 6));

            Cell h = t.Cells[1, 5];
            h.TextString = "Коэфф. потерь";
            h.TextStyleId = ts; h.TextHeight = 25; h.Alignment = CellAlignment.MiddleCenter;
            Num(t, 2, 5, 1.10, "%lu2%pr2", ts);
            Num(t, 3, 5, 1.10, "%lu2%pr2", ts);
            Formula(t, 2, 6, "=C3*D3*E3*F3", ts);
            Formula(t, 3, 6, "=C4*D4*E4*F4", ts);

            for (int r = 0; r < 4; r++)
                for (int c = 0; c < 7; c++)
                {
                    var b = t.Cells[r, c].Borders;
                    b.Top.LineWeight = LineWeight.LineWeight030; b.Bottom.LineWeight = LineWeight.LineWeight030;
                    b.Left.LineWeight = LineWeight.LineWeight030; b.Right.LineWeight = LineWeight.LineWeight030;
                }
            t.GenerateLayout();
            tr.Commit();
        }
        db.EvaluateFields();
        doc.Editor.WriteMessage("\nPAINTK done\n");
    }
}
