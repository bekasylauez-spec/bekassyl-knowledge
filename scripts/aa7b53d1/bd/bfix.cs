using System;
using System.Collections.Generic;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(BFix.Cmd))]
namespace BFix
{
    public class Cmd
    {
        static Autodesk.AutoCAD.EditorInput.Editor ed;
        static void W(string s) { ed.WriteMessage("\n[BFIX] " + s); }
        static ObjectId ById(Database db, string h) { return db.GetObjectId(false, new Handle(Convert.ToInt64(h, 16)), 0); }

        static string Once(string src, string oldS, string newS, string tag)
        {
            int i = src.IndexOf(oldS, StringComparison.Ordinal);
            if (i < 0) throw new System.Exception("NOT FOUND: " + tag);
            if (src.IndexOf(oldS, i + 1, StringComparison.Ordinal) >= 0) throw new System.Exception("NOT UNIQUE: " + tag);
            W("ok " + tag);
            return src.Substring(0, i) + newS + src.Substring(i + oldS.Length);
        }
        static string Span(string src, string startMark, string endMark, string newS, string tag)
        {
            int a = src.IndexOf(startMark, StringComparison.Ordinal);
            if (a < 0) throw new System.Exception("NOT FOUND start: " + tag);
            int b = src.IndexOf(endMark, a, StringComparison.Ordinal);
            if (b < 0) throw new System.Exception("NOT FOUND end: " + tag);
            b += endMark.Length;
            W("ok span " + tag + " [" + src.Substring(a, Math.Min(60, b - a)).Replace("\t", "^I") + "...]");
            return src.Substring(0, a) + newS + src.Substring(b);
        }

        const string T = "\t";
        const string P0 = @"\P\pi0,l0,tz;-" + "\t";

        [CommandMethod("BFIX")]
        public void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            ed = doc.Editor;
            var db = doc.Database;
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    // ---------- 1. Общие данные, левая колонка (1285A9)
                    var od = (MText)tr.GetObject(ById(db, "1285A9"), OpenMode.ForWrite);
                    string s = od.Contents;
                    int a = s.IndexOf("2. Характеристика района строительства:", StringComparison.Ordinal);
                    int a0 = s.LastIndexOf(@"\P\P", a, StringComparison.Ordinal);
                    int b = s.IndexOf(@"\pi2.9542,l0.59167;", a, StringComparison.Ordinal);
                    int b0 = s.LastIndexOf(@"\P", b, StringComparison.Ordinal);
                    if (a < 0 || a0 < 0 || b < 0 || b0 < 0 || a0 > a || b0 < a) throw new System.Exception("section 2 markers");
                    string sec2 =
                        @"\P\P\pi0,l0,tz;2. Характеристика района строительства (по отчёту ИГИ ТОО «ПКФ Таза су», октябрь 2024 г.):"
                        + P0 + "климатический район строительства — IV, подрайон IVГ (СП РК 2.04-01-2017);"
                        + P0 + @"снеговой район — III; характеристическое значение снеговой нагрузки на грунт — 1,5 кПа (годовая вероятность превышения 0,02), расчётное значение при коэффициенте надёжности по нагрузке 1,5 — 2,25 кПа; НТП РК 01-01-3.1(4.1)-2017 (НП к СП РК EN 1991-1-3:2003/2011);"
                        + P0 + @"ветровой район — IV; базовое давление ветра — 0,77 кПа, расчётное значение при коэффициенте надёжности по нагрузке 1,5 — 1,16 кПа; НТП РК 01-01-3.1(4.1)-2017 (НП к СП РК EN 1991-1-4:2005/2011);"
                        + P0 + @"температура воздуха наиболее холодной пятидневки обеспеченностью 0,92 — минус 14,3 \U+00B0С, абсолютная минимальная — минус 30,3 \U+00B0С;"
                        + P0 + @"нормативная глубина сезонного промерзания: суглинки и глины — 0,29 м, супеси, пески мелкие и пылеватые — 0,35 м, пески гравелистые, крупные и средней крупности — 0,38 м, крупнообломочные грунты — 0,43 м; глубина проникновения 0 \U+00B0С в супеси — 0,45 м; максимальная глубина промерзания — 0,75 м;"
                        + P0 + "грунтовые воды выработками глубиной до 3,0 м (октябрь 2024 г.) не вскрыты;"
                        + P0 + @"основание фундаментов — ИГЭ-1 галечник, мощность слоя 1,5 м, плотность 1,90 г/см\U+00B3, условное расчётное сопротивление R0 = 180/150 кПа; ниже залегают ИГЭ-2 — песок мелкий с включением гравия, мощность 1,5 м, и ИГЭ-3 — супесь светло-коричневая от полутвёрдой до мягкопластичной консистенции, мощность 2,9 м;"
                        + P0 + "супеси ИГЭ-3 слабо- и среднепросадочные, начальное просадочное давление 0,05–0,10 МПа (среднее 0,07 МПа), тип грунтовых условий по просадочности — I;"
                        + P0 + "грунты незасолённые (сухой остаток 0,39–0,44 %), агрессивность к бетону и стали — см. «Защита строительных конструкций от коррозии»;"
                        + P0 + @"тип грунтовых условий по сейсмическим свойствам — III; исходная сейсмичность по карте ОСЗ-2475 — 8 баллов (agR = 0,25g), сейсмичность площадки строительства — 9 баллов (табл. 6.2 СП РК 2.03-30-2017), расчётное горизонтальное ускорение 0,229g;"
                        + P0 + "уровень ответственности сооружения — II.";
                    s = s.Substring(0, a0) + sec2 + s.Substring(b0);
                    W("ok section 2");
                    s = Span(s, "Фундаменты под несущие конструкции выполнены", "34028-2016.",
                        "Фундамент — монолитная железобетонная плита толщиной 0,3 м. Бетон С20/25 W6 F150 на сульфатостойком цементе по ГОСТ 22266-2013. Арматура класса А500С по ГОСТ 34028-2016.", "foundation");
                    s = Span(s, "из бетона класса С8/10 W6 F150", "с каждой стороны.",
                        "из бетона класса С8/10 W6 F150 на сульфатостойком цементе, выступающая за габариты плиты на 0,1 м с каждой стороны.", "prep");
                    s = Span(s, "Стены- железобетонные", "34028-2016.",
                        "Стены — монолитные железобетонные, толщиной 0,4 м. Бетон С20/25 W6 F150 на сульфатостойком цементе по ГОСТ 22266-2013. Арматура класса А500С по ГОСТ 34028-2016.", "walls");
                    s = Once(s, "рабочей арматуры колонн и ригелей выполнить и стен при", "рабочей арматуры стен и плит при", "splice");
                    od.Contents = s;

                    // ---------- 2. Общие данные, правая колонка (1285AB)
                    var od2 = (MText)tr.GetObject(ById(db, "1285AB"), OpenMode.ForWrite);
                    s = od2.Contents;
                    s = Once(s, "по грунту ГФ-021 ГОСТ 25129-82* в 1 слой", "по грунтовке ГФ-021 ГОСТ 25129-2020 в 1 слой", "gf1");
                    s = Once(s, "грунтовкой ГФ 021 (ГОСТ 25129-2020) в 2 слоя, затем окрашиваются эмалью ПФ 115 (ГОСТ 6465-76*).",
                                "грунтовкой ГФ-021 (ГОСТ 25129-2020) в 1 слой, затем окрашиваются эмалью ПФ-115 (ГОСТ 6465-76*) в 2 слоя.", "gf2");
                    s = Once(s, "Все металлические конструкции здания", "Все металлические конструкции сооружения", "zd");
                    s = Once(s, "антикоррозийными покрытиями.",
                        @"антикоррозийными покрытиями.\PСтепень агрессивности грунтов (отчёт ИГИ, прил. 6): по содержанию сульфатов SO4 2112–2880 мг/кг для бетонов на портландцементе при W4–W6 — сильноагрессивная, при W8 — среднеагрессивная, на сульфатостойком и шлакопортландцементе — неагрессивная; по содержанию хлоридов Cl 735–927 мг/кг к арматуре при W4–W6 — среднеагрессивная, при W8 — слабоагрессивная. Коррозионная активность грунтов к углеродистой стали — высокая и средняя. Бетон всех монолитных конструкций и подготовки выполнять на сульфатостойком цементе по ГОСТ 22266-2013, без добавок хлоридов.", "aggr");
                    s = Once(s, "АНТИСЕЙСМИЧЕСКАЯ МЕРОПРИЯТИЯ", "АНТИСЕЙСМИЧЕСКИЕ МЕРОПРИЯТИЯ", "antis");
                    od2.Contents = s;

                    // ---------- 3. Лист 30: примечание трапа (14E3E6) + сдвиг вверх вместе с верхним текстом
                    var nt = (MText)tr.GetObject(ById(db, "14E3E6"), OpenMode.ForWrite);
                    double bot0 = nt.GeometricExtents.MinPoint.Y;
                    s = nt.Contents;
                    s = Once(s, "IV классу по ГОСТ 9.032-74*." + T,
                        "IV классу по ГОСТ 9.032-74*." + @"\PПлощадь окраски стальных конструкций трапа - 346 кв.м (поз. 1 - 18,2; поз. 2 - 11,1; поз. 4 - 21,9; поз. 5 - 60,3; поз. 6 - 234,5 кв.м). Расход с учётом потерь 10 %: грунтовка ГФ-021 (236-101-0107), 1 слой 20 мкм, 0,10 кг/кв.м - 38,1 кг; эмаль ПФ-115 (236-203-0109), 2 слоя общей толщиной 50 мкм, 0,12 кг/кв.м на слой - 91,3 кг.", "paint");
                    if (s.EndsWith(@"\P")) s = s.Substring(0, s.Length - 2);
                    nt.Contents = s;
                    double bot1 = nt.GeometricExtents.MinPoint.Y;
                    double dy = bot0 - bot1;
                    W(string.Format("trap note bottom {0:F0} -> {1:F0}, dy={2:F0}", bot0, bot1, dy));
                    // upper note on the same sheet
                    MText up = null;
                    var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        var m = tr.GetObject(id, OpenMode.ForRead) as MText;
                        if (m == null || m.Handle.ToString() == "14E3E6") continue;
                        if (m.Contents.Contains("УКАЗАНИЯ ПО ИЗГОТОВЛЕНИЮ") && Math.Abs(m.Location.X - nt.Location.X) < 3000 && m.Location.Y > nt.Location.Y && m.Location.Y - nt.Location.Y < 30000)
                        { up = m; break; }
                    }
                    if (dy > 4200) throw new System.Exception("note grows too much: " + dy);
                    if (dy > 0)
                    {
                        var v = new Vector3d(0, dy, 0);
                        nt.TransformBy(Matrix3d.Displacement(v));
                        if (up == null) throw new System.Exception("upper note not found");
                        up.UpgradeOpen();
                        up.TransformBy(Matrix3d.Displacement(v));
                        W(string.Format("moved up {0} and 14E3E6 by {1:F0}; upper top now {2:F0}", up.Handle, dy, up.GeometricExtents.MaxPoint.Y));
                    }

                    // ---------- 4. Спецификация трапа (143C4E): удалить строки грунтовки и эмали
                    var tb = (Table)tr.GetObject(ById(db, "143C4E"), OpenMode.ForWrite);
                    int R = tb.Rows.Count, C = tb.Columns.Count;
                    var del = new List<int>();
                    for (int r = 0; r < R; r++)
                        for (int c = 0; c < C; c++)
                        {
                            string t = tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone);
                            if (t.Contains("ГФ-021") || t.Contains("ПФ-115")) { if (!del.Contains(r)) del.Add(r); }
                        }
                    if (del.Count != 2) throw new System.Exception("paint rows found: " + del.Count);
                    del.Sort(); del.Reverse();
                    var before = new List<string>();
                    for (int r = 0; r < R; r++)
                    {
                        if (del.Contains(r)) continue;
                        for (int c = 0; c < C; c++) before.Add(tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone));
                    }
                    double hb = tb.Height;
                    foreach (int r in del) { tb.DeleteRows(r, 1); W("deleted row " + r); }
                    tb.GenerateLayout();
                    tb.RecomputeTableBlock(true);
                    int k = 0, bad = 0;
                    for (int r = 0; r < tb.Rows.Count; r++)
                        for (int c = 0; c < tb.Columns.Count; c++, k++)
                        {
                            string t = tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone);
                            if (t != before[k]) { bad++; W(string.Format("CHANGED {0},{1}: '{2}' -> '{3}'", r, c, before[k], t)); }
                        }
                    W(string.Format("table rows {0}->{1}, height {2:F0}->{3:F0}, changed cells {4}", R, tb.Rows.Count, hb, tb.Height, bad));
                    if (bad > 0) throw new System.Exception("table cells changed");
                    // ---------- 5. Лист 3: примечание о СВОР (12A2C9)
                    var n3 = (MText)tr.GetObject(ById(db, "12A2C9"), OpenMode.ForWrite);
                    s = n3.Contents;
                    if (!s.EndsWith("производителя.}")) throw new System.Exception("sheet3 note end");
                    s = s.Substring(0, s.Length - 1) + @"\P7. Объёмы земляных работ и каменной наброски учтены в СВОР.}";
                    n3.Contents = s; W("ok sheet3");
                    tr.Commit();
                    W("COMMIT");
                }
            }
            catch (System.Exception ex) { W("ABORT " + ex.Message); }
        }
    }
}
