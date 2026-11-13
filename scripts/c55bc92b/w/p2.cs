// probe: face material audit over all DS (mixed-material solids, welds not КМ_уз_шов)
var d = document; var sb = new StringBuilder();
var matName = new Dictionary<long, string>();
Func<ElementId, string> mn = id => { long k = id.Value; string n; if (!matName.TryGetValue(k, out n)) { var m = d.GetElement(id) as Material; n = m == null ? "-" : m.Name; matName[k] = n; } return n; };
var mixed = new SortedDictionary<string, int>(); var wrongWeld = new SortedDictionary<string, int>(); int tot = 0, welds = 0, mixedWelds = 0, nonShovWelds = 0;
var examples = new List<string>();
foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
{
    if (ds.ApplicationId != "БК_узел") continue; string adi = ds.ApplicationDataId ?? ""; string key = adi.Contains("|") ? adi.Split('|')[0].Trim() : adi;
    bool isWeld = ds.Category != null && ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionWelds;
    foreach (var s in QSolidsOf(ds))
    {
        tot++; var set = new HashSet<string>(); foreach (Face f in s.Faces) set.Add(mn(f.MaterialElementId));
        if (isWeld) { welds++; if (set.Count > 1) { mixedWelds++; } if (!(set.Count == 1 && set.Contains("КМ_уз_шов"))) { nonShovWelds++; string k2 = key + " | " + string.Join("+", set.OrderBy(x => x)); int n; wrongWeld.TryGetValue(k2, out n); wrongWeld[k2] = n + 1; if (examples.Count < 12) examples.Add(ds.Id.Value + " " + ds.Name); } }
        if (set.Count > 1) { string k = (isWeld ? "weld " : "part ") + key + " | " + string.Join("+", set.OrderBy(x => x)); int n; mixed.TryGetValue(k, out n); mixed[k] = n + 1; }
    }
}
sb.AppendLine("solids " + tot + ", weld solids " + welds + ", mixed-material welds " + mixedWelds + ", welds not pure КМ_уз_шов " + nonShovWelds);
sb.AppendLine("=== mixed (all) by key:"); foreach (var kv in mixed) sb.AppendLine("  " + kv.Value + "  " + kv.Key);
sb.AppendLine("=== welds not pure шов:"); foreach (var kv in wrongWeld) sb.AppendLine("  " + kv.Value + "  " + kv.Key);
foreach (var e in examples) sb.AppendLine("  ex " + e);
return sb.ToString();
}
