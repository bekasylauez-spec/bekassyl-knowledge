var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var names = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Select(x => x.Name ?? "").Where(n => n.Contains("Р2")).GroupBy(n => n.Length > 30 ? n.Substring(0, 30) : n).Select(g => g.Key + " x" + g.Count());
return string.Join("\n", names.Take(20));
