using System; using System.Collections.Generic; using System.Linq; public class RnP { public string Key="", Loc="", Title="", Cmt=""; public bool Weld, Bolt; } public static class T {
static string RnSteel(string cmt) { var m = System.Text.RegularExpressions.Regex.Match(cmt ?? "", @"(С\d{3}|09Г2С)"); return m.Success ? m.Groups[1].Value : ""; }
// Қайтарады: true = выноска керек; top/bot = жолдар; key = топ кілті; plain = стрелкасыз («Болты …»)
static bool RnLabel(RnP p, out string top, out string bot, out string key, out bool plain) {
    top = ""; bot = ""; key = ""; plain = false; if (p.Weld) return false; string t = p.Title; string tl = t.ToLowerInvariant();
    var mb = System.Text.RegularExpressions.Regex.Match(t, @"М(\d+)");
    bool anchor = tl.Contains("анкер") && !tl.Contains("шайба анкера"); if (!anchor && p.Key.StartsWith("база") && tl.Contains("гайка")) anchor = true;
    if (anchor) { top = "Анкер " + (mb.Success ? "М" + mb.Groups[1].Value : ""); bot = "09Г2С"; key = "anchor"; return true; }
    if (tl.Contains("болт") || tl.Contains("гайка") || tl.Contains("стержень") || tl.Contains("бастиек") || (tl.Contains("шайба") && !tl.Contains("шайба анкера") && !tl.Contains("шайба-пластина"))) {
        if (tl.Contains("гайка") && !tl.Contains("болт")) { top = "Болты " + (mb.Success ? "М" + mb.Groups[1].Value : ""); } else top = "Болты " + (mb.Success ? "М" + mb.Groups[1].Value : "");
        key = "bolt" + (mb.Success ? mb.Groups[1].Value : ""); plain = true; return true; }
    if (tl.Contains("подливка")) { top = "Подливка"; key = "grout"; return true; }
    if (tl.Contains("подколонник")) return false;
    string steel = RnSteel(p.Cmt);
    var mp = System.Text.RegularExpressions.Regex.Match(t, @"I\s?(\d+Б\d?|\d+Ш\d?|\d+М)"); var mc = System.Text.RegularExpressions.Regex.Match(t, @"\[\s?(\d+П?)"); var mr = System.Text.RegularExpressions.Regex.Match(t, @"рельс\s*(Р\d+)");
    var ma = System.Text.RegularExpressions.Regex.Match(t, @"[∟L]\s?(\d{2,3})\s?[×xх]\s?(\d{1,2})"); var mt = System.Text.RegularExpressions.Regex.Match(t, @"[−\-]\s?(\d+(?:[.,]\d+)?)\s?[×xх]");
    if (mr.Success) { top = mr.Groups[1].Value; key = "rail"; return true; }
    if (tl.Contains("уголок") && ma.Success) { top = "L" + ma.Groups[1].Value + "x" + ma.Groups[2].Value; bot = steel; key = "L" + top; return true; }
    if (mp.Success) { top = "двутавр " + mp.Groups[1].Value; bot = steel; key = "I" + mp.Groups[1].Value; return true; }
    if (mc.Success) { top = "[" + mc.Groups[1].Value; bot = steel; key = "C" + mc.Groups[1].Value; return true; }
    if (mt.Success) { top = "−t" + mt.Groups[1].Value.Replace(',', '.'); bot = steel; key = "t" + top + steel + System.Text.RegularExpressions.Regex.Replace(tl, @"[\d×x−\-\.,\s]+", " ").Trim().Split(' ')[0]; return true; }
    string w = t.Split(' ')[0]; if (w.Length == 0) return false; top = char.ToUpper(w[0]) + w.Substring(1); bot = steel; key = "w" + w; return true; }

static string RnTitle(string name, string loc) {
    string t = name ?? ""; int i = t.IndexOf(" - "); if (i >= 0 && (t.StartsWith("Узел") || t.StartsWith("База"))) t = t.Substring(i + 3);
    string suf = " - " + loc; if (loc != "" && t.EndsWith(suf)) t = t.Substring(0, t.Length - suf.Length); return t; }
public static void Main() {
 string[][] tests = { new[]{"узел 1","оголовок −25×320×684","поз.1 оголовок −25×320×684 С345, 6 тесік"}, new[]{"узел 1","болт ВП М24×90 стержень",""}, new[]{"узел 17","уголок L100×7 l200","уголок С245"}, new[]{"узел 6","тіреуіш I25Б1 l250","С245"}, new[]{"узел 6","швеллер [30П l300","С245"}, new[]{"база Б1","анкер М42 L1000 (шартты)",""}, new[]{"база Б1","гайка М42 выверочная",""}, new[]{"база Б1","шайба анкера −20×100×100 (отв. Ø45)","С345"}, new[]{"база Б1","подливка −50×640×870",""}, new[]{"узел 6","брус 200×300×300","брус"}, new[]{"узел 5","рельс Р24 l5000",""}, new[]{"узел 8","гусет −20×200×300","С245"} };
 foreach (var t in tests) { var p = new RnP { Key = t[0], Title = t[1], Cmt = t[2] }; string top, bot, key; bool pl; bool ok = RnLabel(p, out top, out bot, out key, out pl); Console.WriteLine(t[1] + " => " + ok + " | " + top + " / " + bot + " | key " + key + " plain " + pl); }
 Console.WriteLine(RnTitle("Узел 1 - оголовок −25×320×684 - 6-A", "6-A") + " | " + RnTitle("База Б1 - плита −30×640×870 - 6-D", "6-D"));
} }
