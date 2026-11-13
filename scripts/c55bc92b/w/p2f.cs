// probe: face material audit over БК_узел DS (optionally filtered by out\keys.txt); output also to out\mono.txt
var d = document; var sb = new StringBuilder();
string KF = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out\keys.txt";
HashSet<string> KEYS = System.IO.File.Exists(KF) ? new HashSet<string>(System.IO.File.ReadAllLines(KF, Encoding.UTF8).Select(x => x.Trim()).Where(x => x != "")) : null;
var matName = new Dictionary<long, string>();
Func<ElementId, string> mn = id => { long k = id.Value; string n; if (!matName.TryGetValue(k, out n)) { var m = d.GetElement(id) as Material; n = m == null ? "-" : m.Name; matName[k] = n; } return n; };
var mixed = new SortedDictionary<string, int>(); var wrongWeld = new SortedDictionary<string, int>(); int tot = 0, welds = 0, mixedWelds = 0, nonShovWelds = 0;
foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
{
    if (ds.ApplicationId != "БК_узел") continue; string adi = ds.ApplicationDataId ?? ""; string key = adi.Contains("|") ? adi.Split('|')[0].Trim() : adi; string lc0 = adi.Contains("|") ? adi.Split('|')[1].Trim() : "";
    if (KEYS != null && !(KEYS.Contains(key) || KEYS.Contains(key + "|" + lc0))) continue;
    bool isWeld = ds.Category != null && ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionWelds;
    foreach (var s in QSolidsOf(ds))
    {
        tot++; var set = new HashSet<string>(); foreach (Face f in s.Faces) set.Add(mn(f.MaterialElementId));
        if (isWeld) { welds++; if (set.Count > 1) mixedWelds++; if (!(set.Count == 1 && set.Contains("КМ_уз_шов"))) { nonShovWelds++; string k2 = key + " | " + string.Join("+", set.OrderBy(x => x)); int n; wrongWeld.TryGetValue(k2, out n); wrongWeld[k2] = n + 1; } }
        if (set.Count > 1) { string k = (isWeld ? "weld " : "part ") + key + " | " + string.Join("+", set.OrderBy(x => x)); int n; mixed.TryGetValue(k, out n); mixed[k] = n + 1; }
    }
}
sb.AppendLine("solids " + tot + ", weld solids " + welds + ", mixed-material welds " + mixedWelds + ", welds not pure КМ_уз_шов " + nonShovWelds);
sb.AppendLine("=== welds not pure шов:"); foreach (var kv in wrongWeld) sb.AppendLine("  " + kv.Value + "  " + kv.Key);
sb.AppendLine("=== mixed parts (info):"); foreach (var kv in mixed.Where(k => !k.Key.StartsWith("weld"))) sb.AppendLine("  " + kv.Value + "  " + kv.Key);
return sb.ToString();
}
