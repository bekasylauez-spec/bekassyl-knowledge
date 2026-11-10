var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var sb = new System.Text.StringBuilder(); double M = 304.8;
var cnt = new SortedDictionary<string,int>();
foreach (var e in new FilteredElementCollector(nd).OfClass(typeof(DirectShape))) { string nm = e.Name; if (nm.Contains("СВ")) { cnt.TryGetValue(nm, out int c); cnt[nm] = c + 1; } }
foreach (var kv in cnt) sb.AppendLine(kv.Value + " x " + kv.Key);
// all DS with Узел Р1 near braced bays at z 4900-5200 and at 10000-10500: count
int n = 0;
// braced columns list: nodes with name Узел Р1 / Узел Р1 ... in braced zones
return sb.ToString();
