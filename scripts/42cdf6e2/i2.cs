var sb=new System.Text.StringBuilder(); double MM=304.8; var opt=new Options{DetailLevel=ViewDetailLevel.Fine};
Func<Element,Solid> solidOf=e=>{Solid acc=null; foreach(var go in e.get_Geometry(opt)){IEnumerable<GeometryObject> objs=go is GeometryInstance gi?gi.GetInstanceGeometry().Cast<GeometryObject>():new[]{go}; foreach(var o in objs){var s=o as Solid; if(s==null||s.Volume<=1e-9)continue; try{acc=acc==null?s:BooleanOperationsUtils.ExecuteBooleanOperation(acc,s,BooleanOperationsType.Union);}catch{if(acc==null)acc=s;}}} return acc;};
var fr=new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
foreach(var g in fr.GroupBy(f=>f.Symbol.Name)){var t=g.First().Symbol; sb.AppendLine("TYPE "+g.Key+" b="+Math.Round((t.LookupParameter("b")?.AsDouble()??0)*MM,1)+" h="+Math.Round((t.LookupParameter("h")?.AsDouble()??0)*MM,1)+" t="+Math.Round((t.LookupParameter("t")?.AsDouble()??0)*MM,1));}
foreach(var g in fr.GroupBy(f=>f.Symbol.Name)){var m=document.GetElement(g.First().StructuralMaterialId) as Material; var c=m.Color; sb.AppendLine("MAT "+m.Name+" rgb "+c.Red+","+c.Green+","+c.Blue+" transp "+m.Transparency+" shin "+m.Shininess+" smooth "+m.Smoothness);}
var rc=new List<Element>(); foreach(var c in new[]{BuiltInCategory.OST_Floors,BuiltInCategory.OST_Walls,BuiltInCategory.OST_StructuralFoundation}) rc.AddRange(new FilteredElementCollector(document).OfCategory(c).WhereElementIsNotElementType());
var rs=rc.ToDictionary(e=>e.Id.Value,e=>solidOf(e));
int n=0; foreach(var f in fr){var s=solidOf(f); if(s==null)continue; foreach(var e in rc){var r=rs[e.Id.Value]; if(r==null)continue; try{var x=BooleanOperationsUtils.ExecuteBooleanOperation(s,r,BooleanOperationsType.Intersect); if(x!=null&&x.Volume*MM*MM*MM>100){n++; if(n<=12) sb.AppendLine("CLASH "+f.Id.Value+" "+f.Symbol.Name+" x RC "+e.Id.Value+" "+Math.Round(x.Volume*MM*MM*MM/1000,1)+"cm3 @"+Math.Round(x.ComputeCentroid().X*MM)+","+Math.Round(x.ComputeCentroid().Y*MM)+","+Math.Round(x.ComputeCentroid().Z*MM));}}catch{}}}
sb.AppendLine("CLASH total "+n);
var ds=new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(d=>{var k=d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString();return k=="ПЛ1"||k=="ПЛ2";}).ToList();
var sum=new Dictionary<string,int>(); int bad=0;
foreach(var d in ds){var k=d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString(); var bb=d.get_BoundingBox(null); int ns=0,cyl=0; Solid pl=null; foreach(var go in d.get_Geometry(opt)){var s=go as Solid; if(s!=null&&s.Volume>1e-9){ns++; foreach(Face fc in s.Faces) if(fc is CylindricalFace){cyl++;break;} }}
 var dim=new[]{(bb.Max.X-bb.Min.X)*MM,(bb.Max.Y-bb.Min.Y)*MM,(bb.Max.Z-bb.Min.Z)*MM};
 // gap to nearest RC bbox
 double best=1e9; long bid=0; foreach(var e in rc){var eb=e.get_BoundingBox(null); double dx=Math.Max(0,Math.Max(eb.Min.X-bb.Max.X,bb.Min.X-eb.Max.X)),dy=Math.Max(0,Math.Max(eb.Min.Y-bb.Max.Y,bb.Min.Y-eb.Max.Y)),dz=Math.Max(0,Math.Max(eb.Min.Z-bb.Max.Z,bb.Min.Z-eb.Max.Z)); double dd=Math.Sqrt(dx*dx+dy*dy+dz*dz)*MM; if(dd<best){best=dd;bid=e.Id.Value;}}
 string key=k+" dims "+string.Join("x",dim.Select(v=>Math.Round(v)).OrderByDescending(v=>v))+" solids "+ns+" cylSolids "+cyl; if(!sum.ContainsKey(key))sum[key]=0; sum[key]++;
 if(best>0.5){bad++; if(bad<=15) sb.AppendLine("PLATE-GAP "+k+" "+d.Id.Value+" gap "+Math.Round(best,1)+"mm to RC "+bid+" @"+Math.Round(bb.Min.X*MM)+","+Math.Round(bb.Min.Y*MM)+","+Math.Round(bb.Min.Z*MM));}
}
foreach(var kv in sum) sb.AppendLine("PL "+kv.Key+" x"+kv.Value);
sb.AppendLine("plates not touching RC bbox: "+bad);
// posts bottom
foreach(var f in fr.Where(f=>Math.Abs(((LocationCurve)f.Location).Curve.GetEndPoint(1).Z-((LocationCurve)f.Location).Curve.GetEndPoint(0).Z)>0.5)){var c=((LocationCurve)f.Location).Curve; double z0=Math.Min(c.GetEndPoint(0).Z,c.GetEndPoint(1).Z)*MM; var kk=Math.Round(z0); if(f.Symbol.Name=="Кр1")continue; }
return sb.ToString();
}
static void Pad() {