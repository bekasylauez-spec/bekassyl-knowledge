using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

// Second pass on a sheet's geo dump: finds Tekla marks, node callouts, section marks, axes,
// frame and stamp, and writes SPDS ops for the BkSpds plugin. Positions are kept.
public static class Spds
{
    static readonly CultureInfo CI = CultureInfo.InvariantCulture;
    class Ln { public string H; public double X1, Y1, X2, Y2;
        public double Len { get { return Math.Sqrt((X2 - X1) * (X2 - X1) + (Y2 - Y1) * (Y2 - Y1)); } }
        public bool Hor { get { return Math.Abs(Y2 - Y1) < 0.5 && Len > 1; } }
        public bool Ver { get { return Math.Abs(X2 - X1) < 0.5 && Len > 1; } } }
    class Tx { public string H, Style, S; public double X, Y, Ht, Rot; }
    class Pt { public string T, H; public double X, Y; public string Rest; }
    class Ci { public string H; public double X, Y, R; }

    static double D(string s) { return double.Parse(s, CI); }
    static string F(double v) { return v.ToString("0.###", CI); }
    static double Dist(double ax, double ay, double bx, double by) { return Math.Sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by)); }

    public static string Run(string geoPath, string opsPath, double k, double ox, double oy, string sheetNo, string sheetName, double W, double H, double kNew)
    {
        var lines = new List<Ln>(); var texts = new List<Tx>(); var other = new List<Pt>(); var circles = new List<Ci>();
        foreach (var raw in File.ReadAllLines(geoPath, Encoding.GetEncoding(1251)))
        {
            var f = raw.Split('\t');
            var n = f[2].Split(' ').Where(x => x != "").Select(D).ToArray();
            if (f[0] == "L") lines.Add(new Ln { H = f[1], X1 = n[0], Y1 = n[1], X2 = n[2], Y2 = n[3] });
            else if (f[0] == "T") texts.Add(new Tx { H = f[1], X = n[0], Y = n[1], Ht = n[4], Rot = n[5], Style = f[3], S = f.Length > 4 ? f[4] : "" });
            else if (f[0] == "C") circles.Add(new Ci { H = f[1], X = n[0], Y = n[1], R = n[2] });
            else other.Add(new Pt { T = f[0], H = f[1], X = n[0], Y = n[1], Rest = string.Join("\t", f.Skip(3)) });
        }
        // paper coordinates helpers
        Func<double, double> PX = x => (x - ox) / k; Func<double, double> PY = y => (y - oy) / k;
        var used = new HashSet<string>();
        var ops = new StringBuilder();
        Action<string> Del = h => { if (h != null) used.Add(h); };
        Func<double, double, List<Pt>> WipeAt = (x, y) => other.Where(o => o.T == "WI" && Dist(o.X, o.Y, x, y) < 0.3 * k).ToList();

        // ---- frame + stamp + side columns ----
        foreach (var l in lines)
        {
            double x1 = PX(l.X1), y1 = PY(l.Y1), x2 = PX(l.X2), y2 = PY(l.Y2);
            bool frame = l.Len / k > 0.8 * Math.Min(W, H) - 30 && ((l.Hor && (Near(y1, 0) || Near(y1, H) || Near(y1, 5) || Near(y1, H - 5))) || (l.Ver && (Near(x1, 0) || Near(x1, W) || Near(x1, 20) || Near(x1, W - 5))));
            bool inStamp = Math.Min(x1, x2) > W - 190.5 && Math.Max(y1, y2) < 60.5 && Math.Min(y1, y2) > 4.5;
            bool grid = (l.Hor || l.Ver) && l.Len / k >= 4.5;
            bool side = Math.Max(x1, x2) < 20.5 && Math.Min(y1, y2) > 4.5 && Math.Max(y1, y2) < 160;
            if (frame || (inStamp && grid) || (side && (l.Hor || l.Ver))) Del(l.H);
        }
        foreach (var t in texts)
        {
            double x = PX(t.X), y = PY(t.Y);
            bool inStamp = x > W - 190.5 && y < 60.5 && y > 4.5;
            bool changeRow = x < W - 5 - 120 && y > 5 + 30;   // revision rows keep their texts
            bool side = x < 20.5 && y > 4.5 && y < 160;
            bool label = Regex.IsMatch(t.S.Trim(), @"^(Изм\.?|Кол\.?\s*уч\.?|Лист|№\s*док\.?|Подп\.?|Дата)$");
            if ((inStamp && (!changeRow || label)) || side) { Del(t.H); foreach (var w in WipeAt(t.X, t.Y)) Del(w.H); }
        }
        // signatures in the «Подп.» column move one row down: in the user's stamp ГИП is the 3rd row from the bottom
        var sig = lines.Where(l => !used.Contains(l.H) && !(l.Hor || l.Ver) || (!used.Contains(l.H) && l.Len / k < 4.5)).Where(l =>
        { double x = PX(l.X1), y = PY(l.Y1); return x > W - 155 && x < W - 134 && y > 9.5 && y < 30.5; }).Select(l => l.H).ToList();
        if (sig.Count > 0) ops.AppendLine("MOVE\t0 " + F(-5 * kNew) + "\t" + string.Join(" ", sig));
        // what stays of the Tekla stamp (revision row texts, signatures, logo) travels to the new stamp
        var keep = new List<string>(sig);
        keep.AddRange(texts.Where(t => !used.Contains(t.H) && PX(t.X) > W - 190.5 && PY(t.Y) < 60.5 && PY(t.Y) > 4.5).Select(t => t.H));
        keep.AddRange(lines.Where(l => !used.Contains(l.H) && PX(l.X1) > W - 190.5 && PY(l.Y1) < 60.5 && PY(l.Y1) > 4.5).Select(l => l.H));
        keep.AddRange(other.Where(o => o.T == "IM" && PX(o.X) > W - 190.5 && PY(o.Y) < 60.5).Select(o => o.H));
        keep = keep.Distinct().ToList();
        var keepSet = new HashSet<string>(keep);

        // ---- axes: bubble r = 4 mm on paper, text inside, line from the bubble ----
        int nAxis = 0;
        foreach (var c in circles.Where(c => Math.Abs(c.R / k - 4.0) < 0.6))
        {
            var t = texts.FirstOrDefault(x => !used.Contains(x.H) && Dist(x.X, x.Y, c.X, c.Y) < c.R);
            Ln best = null; double bx = 0, by = 0, fx = 0, fy = 0;
            foreach (var l in lines)
            {
                if (used.Contains(l.H) || l.Len < 10 * c.R) continue;
                if (Math.Abs(Dist(l.X1, l.Y1, c.X, c.Y) - c.R) < 2) { best = l; bx = l.X1; by = l.Y1; fx = l.X2; fy = l.Y2; break; }
                if (Math.Abs(Dist(l.X2, l.Y2, c.X, c.Y) - c.R) < 2) { best = l; bx = l.X2; by = l.Y2; fx = l.X1; fy = l.Y1; break; }
            }
            if (t == null || best == null) continue;
            Del(c.H); Del(t.H); Del(best.H); foreach (var w in WipeAt(t.X, t.Y)) Del(w.H);
            ops.AppendLine("AXIS\t" + t.S.Trim() + "\t" + F(bx) + " " + F(by) + " " + F(fx) + " " + F(fy) + "\t" + F(c.R) + "\t" + F(c.X) + " " + F(c.Y));
            nAxis++;
        }

        // ---- node callouts: circle at the node, leader to a shelf with two texts ----
        int nKnot = 0;
        foreach (var c in circles.Where(c => !used.Contains(c.H) && c.R / k > 3.0 && c.R / k < 8.0))
        {
            foreach (var ld in lines.Where(l => !used.Contains(l.H) && !l.Hor && !l.Ver))
            {
                double ax, ay, rx, ry;
                if (Math.Abs(Dist(ld.X1, ld.Y1, c.X, c.Y) - c.R) < 3) { ax = ld.X1; ay = ld.Y1; rx = ld.X2; ry = ld.Y2; }
                else if (Math.Abs(Dist(ld.X2, ld.Y2, c.X, c.Y) - c.R) < 3) { ax = ld.X2; ay = ld.Y2; rx = ld.X1; ry = ld.Y1; }
                else continue;
                var shelf = lines.FirstOrDefault(s => !used.Contains(s.H) && s.Hor && (Dist(s.X1, s.Y1, rx, ry) < 2 || Dist(s.X2, s.Y2, rx, ry) < 2));
                if (shelf == null) continue;
                double sx0 = Math.Min(shelf.X1, shelf.X2), sx1 = Math.Max(shelf.X1, shelf.X2), sy = shelf.Y1;
                var near = texts.Where(t => !used.Contains(t.H) && t.X > sx0 - 2 * t.Ht && t.X < sx1 + t.Ht && Math.Abs(t.Y - sy) < 2.5 * t.Ht).ToList();
                var top = near.Where(t => t.Y > sy).OrderBy(t => t.Y).FirstOrDefault();
                var bot = near.Where(t => t.Y < sy).OrderByDescending(t => t.Y).FirstOrDefault();
                if (top == null) continue;
                Del(c.H); Del(ld.H); Del(shelf.H); Del(top.H); if (bot != null) Del(bot.H);
                foreach (var t in new[] { top, bot }) if (t != null) foreach (var w in WipeAt(t.X, t.Y)) Del(w.H);
                // shelf runs away from the leader end
                double dir = Dist(shelf.X1, shelf.Y1, rx, ry) < 2 ? Math.Sign(shelf.X2 - shelf.X1) : Math.Sign(shelf.X1 - shelf.X2);
                ops.AppendLine("KNOT\t" + top.S.Trim() + "\t" + (bot == null ? "" : bot.S.Trim()) + "\t" + F(c.X) + " " + F(c.Y) + " " + F(c.R) + " " + F(rx) + " " + F(ry) + " " + F(dir) + " " + F(Math.Abs(sx1 - sx0)));
                nKnot++;
                break;
            }
        }

        // ---- section marks: filled arrow + stroke + label ----
        var secs = new List<Tuple<string, double, double, double, double, List<string>>>(); var ends = new Dictionary<int, double[]>();   // word, strokeX, strokeY, arrow dx, dy, handles
        foreach (var ha in other.Where(o => (o.T == "HA" || o.T == "SO") && !used.Contains(o.H)))
        {
            // arrow head = two lines meeting at the tip, starting near the hatch
            var heads = lines.Where(l => !used.Contains(l.H) && !l.Hor && !l.Ver && l.Len / k < 6 && (Dist(l.X1, l.Y1, ha.X, ha.Y) < 0.3 * k || Dist(l.X2, l.Y2, ha.X, ha.Y) < 0.3 * k)).ToList();
            if (heads.Count == 0) continue;
            var h0 = heads[0];
            double tx = Dist(h0.X1, h0.Y1, ha.X, ha.Y) < 0.3 * k ? h0.X2 : h0.X1, ty = Dist(h0.X1, h0.Y1, ha.X, ha.Y) < 0.3 * k ? h0.Y2 : h0.Y1;
            var arrowLines = lines.Where(l => !used.Contains(l.H) && (Dist(l.X1, l.Y1, tx, ty) < 2 || Dist(l.X2, l.Y2, tx, ty) < 2) && !l.Ver && !l.Hor).ToList();
            // arrow direction: from the base (hatch corner side) to the tip
            double bdx = tx - ha.X, bdy = ty - ha.Y, bl = Math.Sqrt(bdx * bdx + bdy * bdy); bdx /= bl; bdy /= bl;
            bool alongX = Math.Abs(bdx) > Math.Abs(bdy);
            var shaft = lines.FirstOrDefault(l => !used.Contains(l.H) && (alongX ? l.Hor : l.Ver) && l.Len / k < 12 && DistToSeg(tx, ty, l) < 2.0 * k);
            var stroke = lines.FirstOrDefault(l => !used.Contains(l.H) && (alongX ? l.Ver : l.Hor) && l.Len / k < 8 && l.Len / k > 2 && DistToSeg(tx, ty, l) < 2);
            if (stroke == null) continue;
            var lab = texts.Where(t => !used.Contains(t.H) && t.Ht / kNew > 3.2 && Dist(t.X, t.Y, tx, ty) < 12 * k && Regex.IsMatch(t.S.Trim(), @"^[0-9А-Яа-яA-Za-z]{1,3}$")).OrderBy(t => Dist(t.X, t.Y, tx, ty)).FirstOrDefault();
            if (lab == null) continue;
            double ax = alongX ? Math.Sign(bdx) : 0, ay = alongX ? 0 : Math.Sign(bdy);
            var hs = new List<string> { ha.H, stroke.H, lab.H };
            hs.AddRange(arrowLines.Select(l => l.H)); hs.AddRange(heads.Select(l => l.H)); if (shaft != null) hs.Add(shaft.H);
            foreach (var l in lines.Where(l => !used.Contains(l.H) && l.Len < 1 && Dist(l.X1, l.Y1, tx, ty) < 12 * k)) hs.Add(l.H);
            // arrow base: short line through the hatch corner
            foreach (var l in lines.Where(l => !used.Contains(l.H) && l.Len / k < 2 && (Dist(l.X1, l.Y1, ha.X, ha.Y) < 0.3 * k || Dist(l.X2, l.Y2, ha.X, ha.Y) < 0.3 * k))) hs.Add(l.H);
            hs.AddRange(WipeAt(lab.X, lab.Y).Select(w => w.H));
            foreach (var h in hs) Del(h);
            double scx = (stroke.X1 + stroke.X2) / 2, scy = (stroke.Y1 + stroke.Y2) / 2;
            ends[secs.Count] = new[] { stroke.X1, stroke.Y1, stroke.X2, stroke.Y2 };
            secs.Add(Tuple.Create(lab.S.Trim(), scx, scy, ax, ay, hs));
        }
        int nSec = 0;
        foreach (var g in secs.GroupBy(s => s.Item1))
        {
            var l = g.ToList();
            if (l.Count >= 2)
            {
                var a = l[0]; var b = l[1];
                var ea = ends[secs.IndexOf(a)]; var eb = ends[secs.IndexOf(b)];
                // the cut line runs between the outer stroke ends
                double ax1 = Dist(ea[0], ea[1], b.Item2, b.Item3) > Dist(ea[2], ea[3], b.Item2, b.Item3) ? ea[0] : ea[2];
                double ay1 = Dist(ea[0], ea[1], b.Item2, b.Item3) > Dist(ea[2], ea[3], b.Item2, b.Item3) ? ea[1] : ea[3];
                double bx1 = Dist(eb[0], eb[1], a.Item2, a.Item3) > Dist(eb[2], eb[3], a.Item2, a.Item3) ? eb[0] : eb[2];
                double by1 = Dist(eb[0], eb[1], a.Item2, a.Item3) > Dist(eb[2], eb[3], a.Item2, a.Item3) ? eb[1] : eb[3];
                // SPDS stroke is ~10 mm and runs inwards from the point: push both ends out so the inner end stays where Tekla had it
                { double ux = bx1 - ax1, uy = by1 - ay1, ul = Math.Sqrt(ux * ux + uy * uy); ux /= ul; uy /= ul; double sh = 5.1 * kNew;
                  ax1 -= ux * sh; ay1 -= uy * sh; bx1 += ux * sh; by1 += uy * sh; }
                double vx = b.Item2 - a.Item2, vy = b.Item3 - a.Item3;
                double cr = vx * a.Item5 - vy * a.Item4;   // arrow to the left (+) or right (-) of a->b
                ops.AppendLine("SECT\t" + g.Key + "\t" + F(ax1) + " " + F(ay1) + " " + F(bx1) + " " + F(by1) + "\t" + (cr > 0 ? "1" : "-1"));
            }
            else { var a = l[0]; ops.AppendLine("SECT1\t" + g.Key + "\t" + F(a.Item2) + " " + F(a.Item3) + " " + F(a.Item4) + " " + F(a.Item5)); }
            nSec++;
        }

        // ---- marks: text on a short shelf with a leader from one shelf end ----
        int nMark = 0;
        var markRx = new Regex(@"^[A-Za-zА-Яа-я][A-Za-zА-Яа-я0-9\-\.]{0,5}$");
        foreach (var t in texts.Where(t => !used.Contains(t.H) && Math.Abs(t.Rot) < 1e-3 && markRx.IsMatch(t.S.Trim())))
        {
            var shelf = lines.FirstOrDefault(l => !used.Contains(l.H) && l.Hor && l.Y1 < t.Y && t.Y - l.Y1 < 0.6 * t.Ht
                        && Math.Min(l.X1, l.X2) <= t.X + 0.2 * t.Ht && Math.Max(l.X1, l.X2) >= t.X + 0.3 * t.Ht && l.Len / k < 15);
            if (shelf == null) continue;
            Ln leader = null; double ox2 = 0, oy2 = 0, tipx = 0, tipy = 0;
            foreach (var p in new[] { new[] { shelf.X1, shelf.Y1, shelf.X2, shelf.Y2 }, new[] { shelf.X2, shelf.Y2, shelf.X1, shelf.Y1 } })
            {
                leader = lines.FirstOrDefault(l => !used.Contains(l.H) && l != shelf && !l.Hor && (Dist(l.X1, l.Y1, p[0], p[1]) < 2 || Dist(l.X2, l.Y2, p[0], p[1]) < 2));
                if (leader != null) { ox2 = p[0]; oy2 = p[1]; bool s1 = Dist(leader.X1, leader.Y1, p[0], p[1]) < 2; tipx = s1 ? leader.X2 : leader.X1; tipy = s1 ? leader.Y2 : leader.Y1; break; }
            }
            if (leader == null) continue;
            double otherEnd = Dist(shelf.X1, shelf.Y1, ox2, oy2) < 2 ? shelf.X2 : shelf.X1;
            double ang = otherEnd > ox2 ? 0 : Math.PI;
            Del(t.H); Del(shelf.H); Del(leader.H); foreach (var w in WipeAt(t.X, t.Y)) Del(w.H);
            ops.AppendLine("MARK\t" + t.S.Trim() + "\t" + F(ox2) + " " + F(oy2) + " " + F(ang) + " " + F(tipx) + " " + F(tipy));
            nMark++;
        }

        // ---- new frame: smallest Цех-type format that holds the content at the new scale ----
        double minX = double.MaxValue, minY = double.MaxValue, maxX = double.MinValue, maxY = double.MinValue;
        Action<double, double> B = (x, y) => { minX = Math.Min(minX, x); minY = Math.Min(minY, y); maxX = Math.Max(maxX, x); maxY = Math.Max(maxY, y); };
        foreach (var l in lines) if (!used.Contains(l.H) && !keepSet.Contains(l.H)) { B(l.X1, l.Y1); B(l.X2, l.Y2); }
        foreach (var t in texts) if (!used.Contains(t.H) && !keepSet.Contains(t.H)) { B(t.X, t.Y); B(t.X + t.S.Length * 0.6 * t.Ht, t.Y + t.Ht); }
        foreach (var c in circles) if (!used.Contains(c.H)) { B(c.X - c.R, c.Y - c.R); B(c.X + c.R, c.Y + c.R); }
        double cw = (maxX - minX) / kNew, ch = (maxY - minY) / kNew;
        var fmts = new[] { Tuple.Create("A3", 1, 420.0, 297.0), Tuple.Create("A2", 1, 594.0, 420.0), Tuple.Create("A3", 3, 891.0, 420.0),
                           Tuple.Create("A3", 4, 1189.0, 420.0), Tuple.Create("A1", 1, 841.0, 594.0), Tuple.Create("A3", 5, 1486.0, 420.0),
                           Tuple.Create("A2", 3, 1261.0, 594.0), Tuple.Create("A0", 1, 1189.0, 841.0), Tuple.Create("A1", 3, 1783.0, 841.0) };
        Tuple<string, int, double, double> pick = null; bool beside = false;
        foreach (var fm in fmts.OrderBy(f => f.Item3 * f.Item4))
        {
            double iw = fm.Item3 - 25 - 10, ih = fm.Item4 - 10 - 10;
            if (cw <= iw && ch + 60 <= ih) { pick = fm; beside = false; break; }      // content above the stamp
            if (cw <= iw - 190 && ch <= ih) { pick = fm; beside = true; break; }      // content left of the stamp
        }
        if (pick == null) pick = fmts.Last();
        double fw = pick.Item3, fh = pick.Item4;
        double nox = minX - (20 + 5 + ((beside ? fw - 25 - 10 - 190 : fw - 25 - 10) - cw) / 2) * kNew;
        double noy = minY - (5 + 5 + (beside ? 0 : 60) + ((beside ? fh - 20 : fh - 20 - 60) - ch) / 2) * kNew;
        if (Math.Abs(kNew - k) < 1e-6)
        {
            // same scale: the user's frame takes the Tekla frame's place and size
            pick = fmts.First(f => Math.Abs(f.Item3 - W) < 3 && Math.Abs(f.Item4 - H) < 3);
            fw = W; fh = H; nox = ox; noy = oy;
        }
        var hdr = new StringBuilder();
        hdr.AppendLine("FRAME\t" + F(nox) + " " + F(noy) + "\t" + F(kNew) + "\t" + pick.Item1 + "x" + pick.Item2 + "\t" + sheetNo + "\t" + sheetName + "\t" + F(fw) + " " + F(fh));
        if (keep.Count > 0)
        {
            // old stamp corner -> new stamp corner, scaled by kNew / k
            hdr.AppendLine("XFORM\t" + F(ox + (W - 5) * k) + " " + F(oy + 5 * k) + "\t" + F(kNew / k) + "\t" + F(nox + (fw - 5) * kNew) + " " + F(noy + 5 * kNew) + "\t" + string.Join(" ", keep));
        }
        ops.Insert(0, hdr.ToString());
        ops.AppendLine("ERASE\t" + string.Join(" ", used));
        File.WriteAllText(opsPath, ops.ToString(), Encoding.UTF8);
        return "axes " + nAxis + ", knots " + nKnot + ", sections " + nSec + ", marks " + nMark + ", erase " + used.Count;
    }

    static bool Near(double a, double b) { return Math.Abs(a - b) < 0.6; }
    static double DistToSeg(double px, double py, Ln l)
    {
        double dx = l.X2 - l.X1, dy = l.Y2 - l.Y1, L2 = dx * dx + dy * dy; if (L2 < 1e-9) return Dist(px, py, l.X1, l.Y1);
        double t = Math.Max(0, Math.Min(1, ((px - l.X1) * dx + (py - l.Y1) * dy) / L2));
        return Dist(px, py, l.X1 + t * dx, l.Y1 + t * dy);
    }
}
