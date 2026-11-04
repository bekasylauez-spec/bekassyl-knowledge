using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

// Reads a geo dump of one sheet (geo.lsp), finds exploded Tekla dimensions and
// writes an ops file for apply.lsp. Positions of dimension lines and texts are kept.
public static class Restyle
{
    static readonly CultureInfo CI = CultureInfo.InvariantCulture;

    public class Ln { public string H; public double X1, Y1, X2, Y2; public bool Used;
        public double Len { get { return Math.Sqrt((X2 - X1) * (X2 - X1) + (Y2 - Y1) * (Y2 - Y1)); } } }
    public class Tx { public string H, Style, S; public double X, Y, AX, AY, Ht, Rot, W, Obl; public int HA, VA; public bool Used; }
    public class Wo { public string H; public double X, Y; }
    public class Ci { public string H; public double X, Y, R; }

    static double D(string s) { return double.Parse(s, CI); }
    static string F(double v) { return v.ToString("0.####", CI); }

    public static string Run(string geoPath, string opsPath, double k, string dimStyle)
    {
        var lines = new List<Ln>(); var texts = new List<Tx>(); var wos = new List<Wo>(); var circles = new List<Ci>();
        foreach (var raw in File.ReadAllLines(geoPath, Encoding.GetEncoding(1251)))
        {
            var f = raw.Split('\t');
            if (f[0] == "L") { var n = f[2].Split(' ').Select(D).ToArray(); lines.Add(new Ln { H = f[1], X1 = n[0], Y1 = n[1], X2 = n[2], Y2 = n[3] }); }
            else if (f[0] == "T") { var n = f[2].Split(' ').Select(D).ToArray();
                texts.Add(new Tx { H = f[1], X = n[0], Y = n[1], AX = n[2], AY = n[3], Ht = n[4], Rot = n[5], W = n[6], Obl = n[7], HA = (int)n[8], VA = (int)n[9], Style = f[3], S = f.Length > 4 ? f[4] : "" }); }
            else if (f[0] == "WI") { var n = f[2].Split(' ').Select(D).ToArray(); wos.Add(new Wo { H = f[1], X = n[0], Y = n[1] }); }
            else if (f[0] == "C") { var n = f[2].Split(' ').Select(D).ToArray(); circles.Add(new Ci { H = f[1], X = n[0], Y = n[1], R = n[2] }); }
        }
        var ops = new StringBuilder(); var log = new StringBuilder();
        int found = 0, missed = 0;
        var numRx = new Regex(@"^\s*(\d+)\s*$");

        foreach (var t in texts)
        {
            var m = numRx.Match(t.S); if (!m.Success) continue;
            double V = double.Parse(m.Groups[1].Value, CI);
            double ux = Math.Cos(t.Rot), uy = Math.Sin(t.Rot), nx = -uy, ny = ux;
            // approximate text centre along u (GOST type A ~0.64h per glyph)
            double tw = t.S.Trim().Length * 0.64 * t.Ht * t.W;
            double bx = t.HA == 0 ? t.X : t.AX, by = t.HA == 0 ? t.Y : t.AY;
            double cu = (bx * ux + by * uy) + (t.HA == 0 ? tw / 2 : t.HA == 2 ? -tw / 2 : 0);
            double cn = bx * nx + by * ny;
            Ln best = null; double bestScore = double.MaxValue; double ba = 0, bb = 0, boff = 0;
            foreach (var l in lines)
            {
                double dx = l.X2 - l.X1, dy = l.Y2 - l.Y1, L = l.Len; if (L < 1) continue;
                if (Math.Abs(dx * uy - dy * ux) / L > 1e-3) continue;      // parallel
                if (Math.Abs(L - V) > 0.6) continue;                        // length equals the value
                double off = cn - (l.X1 * nx + l.Y1 * ny);                  // text above the line
                if (off < -0.3 * t.Ht || off > 2.0 * t.Ht) continue;
                double a = l.X1 * ux + l.Y1 * uy, b = l.X2 * ux + l.Y2 * uy; if (a > b) { var q = a; a = b; b = q; }
                double outside = cu < a ? a - cu : cu > b ? cu - b : 0;
                if (outside > 6 * t.Ht) continue;
                double score = outside + Math.Abs(off - 0.4 * t.Ht);
                if (score < bestScore) { bestScore = score; best = l; ba = a; bb = b; boff = off; }
            }
            if (best == null) { missed++; log.AppendLine("MISS " + t.H + " " + t.S + " at " + F(t.X) + "," + F(t.Y)); continue; }
            found++;
            // dim line ends in world coords (sorted along u)
            double p1x, p1y, p2x, p2y;
            if (best.X1 * ux + best.Y1 * uy <= best.X2 * ux + best.Y2 * uy) { p1x = best.X1; p1y = best.Y1; p2x = best.X2; p2y = best.Y2; }
            else { p1x = best.X2; p1y = best.Y2; p2x = best.X1; p2y = best.Y1; }
            var del = new List<string> { best.H, t.H };
            var d1 = Ext(lines, p1x, p1y, ux, uy, nx, ny, t.Ht, del);
            var d2 = Ext(lines, p2x, p2y, ux, uy, nx, ny, t.Ht, del);
            Ticks(lines, p1x, p1y, ux, uy, t.Ht, del); Ticks(lines, p2x, p2y, ux, uy, t.Ht, del);
            foreach (var w in wos) if (Math.Abs(w.X - t.X) < 0.5 * t.Ht && Math.Abs(w.Y - t.Y) < 0.5 * t.Ht) del.Add(w.H);
            bool moved = cu < ba || cu > bb || Math.Abs(cu - (ba + bb) / 2) > 0.25 * (bb - ba) + t.Ht;
            // text middle point (for moved text) in world coords
            double tmx = cu * ux + (cn + 0.5 * t.Ht) * nx, tmy = cu * uy + (cn + 0.5 * t.Ht) * ny;
            ops.Append("DIM\t" + F(d1[0]) + " " + F(d1[1]) + " " + F(d2[0]) + " " + F(d2[1]) + " " + F(p1x) + " " + F(p1y) + " " + F(Math.Round(t.Rot * 180 / Math.PI, 3))
                + "\t" + dimStyle + "\t" + (d1[2] > 0 ? "1" : "0") + " " + (d2[2] > 0 ? "1" : "0")
                + "\t" + (moved ? F(tmx) + " " + F(tmy) : "-") + "\t" + string.Join(" ", del.Distinct()) + "\n");
        }
        // every other text: own font (Р“РћРЎРў 2.304 = ISOCPEUR italic), paper height snapped to 2.5 / 3.5 / 5 / 7 mm
        var dimTexts = new HashSet<string>(Regex.Matches(ops.ToString(), @"\S+").Cast<Match>().Select(x => x.Value));
        int nt = 0;
        foreach (var t in texts)
        {
            if (dimTexts.Contains(t.H) || t.S.Trim().Length == 0) continue;
            if (t.S.IndexOf("Tekla", StringComparison.OrdinalIgnoreCase) >= 0) { ops.Append("DEL\t" + t.H + "\n"); continue; }
            double hp = t.Ht / k, np = hp < 2.2 ? hp : hp < 3.0 ? 2.5 : hp < 4.25 ? 3.5 : hp < 6.0 ? 5.0 : 7.0;
            ops.Append("TXT\t" + t.H + "\t" + F(np * k) + "\n"); nt++;
        }
        // axis lines: lines that start on an axis bubble (r = 4 mm on paper)
        int na = 0;
        foreach (var c in circles.Where(c => Math.Abs(c.R / k - 4.0) < 0.6))
            foreach (var l in lines)
            {
                double d1 = Math.Sqrt((l.X1 - c.X) * (l.X1 - c.X) + (l.Y1 - c.Y) * (l.Y1 - c.Y));
                double d2 = Math.Sqrt((l.X2 - c.X) * (l.X2 - c.X) + (l.Y2 - c.Y) * (l.Y2 - c.Y));
                if ((Math.Abs(d1 - c.R) < 2 || Math.Abs(d2 - c.R) < 2) && l.Len > 10 * c.R && !dimTexts.Contains(l.H))
                { ops.Append("LT\t" + l.H + "\t0.5\n"); na++; }
            }
        File.WriteAllText(opsPath, ops.ToString(), Encoding.GetEncoding(1251));
        File.WriteAllText(opsPath + ".log", log.ToString(), Encoding.GetEncoding(1251));
        return "dims found " + found + ", missed " + missed + ", texts " + nt + ", axis lines " + na;
    }

    // extension line through the dim end: returns defpoint (x,y) and flag 1 if a short ext line was found
    static double[] Ext(List<Ln> lines, double px, double py, double ux, double uy, double nx, double ny, double h, List<string> del)
    {
        foreach (var l in lines)
        {
            double dx = l.X2 - l.X1, dy = l.Y2 - l.Y1, L = l.Len; if (L < 1 || L > 40 * h) continue;
            if (Math.Abs(dx * ux + dy * uy) / L > 1e-3) continue;   // perpendicular
            double along = (l.X1 - px) * ux + (l.Y1 - py) * uy; if (Math.Abs(along) > 0.5) continue;
            double s1 = (l.X1 - px) * nx + (l.Y1 - py) * ny, s2 = (l.X2 - px) * nx + (l.Y2 - py) * ny;
            if (Math.Min(s1, s2) > 0.5 || Math.Max(s1, s2) < -0.5) continue;   // must cross the dim end
            del.Add(l.H);
            double far = Math.Abs(s1) > Math.Abs(s2) ? s1 : s2;
            return new[] { px + far * nx, py + far * ny, 1 };
        }
        return new[] { px, py, 0 };
    }

    static void Ticks(List<Ln> lines, double px, double py, double ux, double uy, double h, List<string> del)
    {
        foreach (var l in lines)
        {
            double L = l.Len; if (L < 0.2 * h || L > 1.5 * h) continue;
            double mx = (l.X1 + l.X2) / 2, my = (l.Y1 + l.Y2) / 2;
            if (Math.Abs(mx - px) > 1 || Math.Abs(my - py) > 1) continue;
            double c = Math.Abs(((l.X2 - l.X1) * ux + (l.Y2 - l.Y1) * uy) / L);
            if (c > 0.2 && c < 0.98) del.Add(l.H);
        }
    }
}

