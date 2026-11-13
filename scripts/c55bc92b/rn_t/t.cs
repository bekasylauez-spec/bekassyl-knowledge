using System; using System.Collections.Generic; using System.Linq; public static class T {
static List<double[]> RnHull(List<double[]> pts) {
    var p = pts.OrderBy(a => a[0]).ThenBy(a => a[1]).ToList(); if (p.Count < 3) return p;
    Func<double[], double[], double[], double> cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    var h = new List<double[]>();
    foreach (var q in p) { while (h.Count >= 2 && cr(h[h.Count - 2], h[h.Count - 1], q) <= 1e-9) h.RemoveAt(h.Count - 1); h.Add(q); }
    int lo = h.Count + 1;
    for (int i = p.Count - 2; i >= 0; i--) { var q = p[i]; while (h.Count >= lo && cr(h[h.Count - 2], h[h.Count - 1], q) <= 1e-9) h.RemoveAt(h.Count - 1); h.Add(q); }
    h.RemoveAt(h.Count - 1); return h; }
static double RnOri(double ax, double ay, double bx, double by, double cx, double cy) { return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax); }
static bool RnSegSeg(double ax, double ay, double bx, double by, double cx, double cy, double dx, double dy) {
    double o1 = RnOri(ax, ay, bx, by, cx, cy), o2 = RnOri(ax, ay, bx, by, dx, dy), o3 = RnOri(cx, cy, dx, dy, ax, ay), o4 = RnOri(cx, cy, dx, dy, bx, by);
    return ((o1 > 0 && o2 < 0) || (o1 < 0 && o2 > 0)) && ((o3 > 0 && o4 < 0) || (o3 < 0 && o4 > 0)); }
static bool RnInRect(double x, double y, double[] r) { return x >= r[0] && x <= r[2] && y >= r[1] && y <= r[3]; }
static bool RnSegRect(double ax, double ay, double bx, double by, double[] r) {   // r = {u0, v0, u1, v1}
    if (RnInRect(ax, ay, r) || RnInRect(bx, by, r)) return true;
    return RnSegSeg(ax, ay, bx, by, r[0], r[1], r[2], r[1]) || RnSegSeg(ax, ay, bx, by, r[2], r[1], r[2], r[3]) || RnSegSeg(ax, ay, bx, by, r[2], r[3], r[0], r[3]) || RnSegSeg(ax, ay, bx, by, r[0], r[3], r[0], r[1]); }
static bool RnRectRect(double[] a, double[] b, double gap) { return !(a[0] > b[2] + gap || b[0] > a[2] + gap || a[1] > b[3] + gap || b[1] > a[3] + gap); }
static bool RnInPoly(double x, double y, List<double[]> h) {   // дөңес көпбұрыш (CCW)
    if (h.Count < 3) return false; for (int i = 0; i < h.Count; i++) { var a = h[i]; var b = h[(i + 1) % h.Count]; if (RnOri(a[0], a[1], b[0], b[1], x, y) < -1e-9) return false; } return true; }
static bool RnPolyRect(List<double[]> h, double[] r) {
    if (h.Count == 0) return false;
    if (h.Count < 3) { if (h.Count == 1) return RnInRect(h[0][0], h[0][1], r); return RnSegRect(h[0][0], h[0][1], h[1][0], h[1][1], r); }
    foreach (var p in h) if (RnInRect(p[0], p[1], r)) return true;
    if (RnInPoly(r[0], r[1], h) || RnInPoly(r[2], r[1], h) || RnInPoly(r[2], r[3], h) || RnInPoly(r[0], r[3], h)) return true;
    for (int i = 0; i < h.Count; i++) { var a = h[i]; var b = h[(i + 1) % h.Count]; if (RnSegRect(a[0], a[1], b[0], b[1], r)) return true; }
    return false; }
static bool RnSegPoly(double ax, double ay, double bx, double by, List<double[]> h) {
    if (h.Count < 2) return false; if (h.Count == 2) return RnSegSeg(ax, ay, bx, by, h[0][0], h[0][1], h[1][0], h[1][1]);
    if (RnInPoly(ax, ay, h) || RnInPoly(bx, by, h)) return true;
    for (int i = 0; i < h.Count; i++) { var a = h[i]; var b = h[(i + 1) % h.Count]; if (RnSegSeg(ax, ay, bx, by, a[0], a[1], b[0], b[1])) return true; } return false; }
static double RnDistPtSeg(double px, double py, double ax, double ay, double bx, double by) {
    double dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy; double t = L2 < 1e-9 ? 0 : Math.Max(0, Math.Min(1, ((px - ax) * dx + (py - ay) * dy) / L2));
    double qx = ax + t * dx, qy = ay + t * dy; return Math.Sqrt((px - qx) * (px - qx) + (py - qy) * (py - qy)); }
static double RnDistPtPoly(double px, double py, List<double[]> h) {
    if (h.Count == 0) return 1e9; if (h.Count == 1) return Math.Sqrt((px - h[0][0]) * (px - h[0][0]) + (py - h[0][1]) * (py - h[0][1]));
    double best = 1e9; for (int i = 0; i < h.Count; i++) { var a = h[i]; var b = h[(i + 1) % h.Count]; best = Math.Min(best, RnDistPtSeg(px, py, a[0], a[1], b[0], b[1])); } return best; }

public static void Main() {
  var pts = new List<double[]> { new[]{0.0,0}, new[]{10.0,0}, new[]{10.0,5}, new[]{0.0,5}, new[]{5.0,2} };
  var h = RnHull(pts); Console.WriteLine("hull " + h.Count + " (exp 4)");
  Console.WriteLine("polyrect inside " + RnPolyRect(h, new[]{4.0,1,6,3}) + " (T), outside " + RnPolyRect(h, new[]{20.0,20,30,30}) + " (F), touch " + RnPolyRect(h, new[]{9.0,4,15,9}) + " (T), crossing-only " + RnPolyRect(h, new[]{-5.0,2,15,3}) + " (T)");
  Console.WriteLine("segseg cross " + RnSegSeg(0,0,10,10,0,10,10,0) + " (T) / par " + RnSegSeg(0,0,10,0,0,1,10,1) + " (F)");
  Console.WriteLine("segpoly " + RnSegPoly(-5,2,15,2,h) + " (T) " + RnSegPoly(-5,20,15,20,h) + " (F)");
  Console.WriteLine("dist " + RnDistPtPoly(15,2,h) + " (5) inpoly " + RnInPoly(3,3,h) + " (T)");
  Console.WriteLine("rectrect " + RnRectRect(new[]{0.0,0,5,5}, new[]{6.0,0,9,5}, 0) + " (F) gap2 " + RnRectRect(new[]{0.0,0,5,5}, new[]{6.0,0,9,5}, 2) + " (T)");
}
}
