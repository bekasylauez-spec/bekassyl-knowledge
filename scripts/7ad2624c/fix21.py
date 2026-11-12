root = 'D:\\Бекасыл КЖ КМ\\Завод_В113_КМ\\_авто\\'
p = root + 'v113_plans.cs'; s = open(p, encoding='utf-8').read()
old = 'foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.Name.StartsWith("База ")))'
new = ('// 13.11: after №117 a base is several bodies (plate / ribs / traverses / washers, one material each) — one mark per base: the plate body only\n'
       '          Func<DirectShape, string> mat0 = x => { foreach (var go in x.get_Geometry(new Options())) { var so = go as Solid; if (so != null && so.Faces.Size > 0) return (d.GetElement(so.Faces.get_Item(0).MaterialElementId) as Material)?.Name ?? ""; } return ""; };\n'
       '          foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.Name.StartsWith("База ") && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && mat0(x) == "КМ_уз_плита"))')
assert old in s; s = s.replace(old, new, 1); open(p, 'w', encoding='utf-8').write(s)
p = root + 'v113_hide_node_marks.cs'; s = open(p, encoding='utf-8').read()
old = 'foreach (var id in s.GetAllPlacedViews()) keep.Add(d.GetElement(id).Name);'
new = 'foreach (var id in s.GetAllPlacedViews()) { var nm = d.GetElement(id).Name; if (!nm.StartsWith("КМ Развертка")) keep.Add(nm); }   // 13.11: the elevation marks (detail number 1) showed as extra «1» on sheets 3 / 6'
assert old in s; s = s.replace(old, new, 1); open(p, 'w', encoding='utf-8').write(s)
print('ok')
