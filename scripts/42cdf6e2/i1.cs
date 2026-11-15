var sb=new System.Text.StringBuilder(); double MM=304.8;
foreach(var c in new[]{BuiltInCategory.OST_Floors,BuiltInCategory.OST_Walls,BuiltInCategory.OST_StructuralFoundation,BuiltInCategory.OST_GenericModel,BuiltInCategory.OST_StructuralColumns,BuiltInCategory.OST_Roofs}){
 var l=new FilteredElementCollector(document).OfCategory(c).WhereElementIsNotElementType().ToList(); sb.AppendLine(c+" "+l.Count);
 foreach(var e in l.Take(14)){var bb=e.get_BoundingBox(null); sb.AppendLine("  "+e.Id.Value+" "+e.Name+" "+(bb==null?"":Math.Round(bb.Min.X*MM)+","+Math.Round(bb.Min.Y*MM)+","+Math.Round(bb.Min.Z*MM)+" - "+Math.Round(bb.Max.X*MM)+","+Math.Round(bb.Max.Y*MM)+","+Math.Round(bb.Max.Z*MM)));}
}
var fr=new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
foreach(var g in fr.GroupBy(f=>f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString()+" | "+f.Symbol.Name+" | "+((document.GetElement(f.StructuralMaterialId) as Material)?.Name))) sb.AppendLine(g.Key+" x"+g.Count());
var ds=new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
foreach(var g in ds.GroupBy(d=>d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString())) sb.AppendLine("DS "+g.Key+" x"+g.Count());
return sb.ToString();
}
static void Pad() {