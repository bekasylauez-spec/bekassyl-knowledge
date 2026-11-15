var sb=new System.Text.StringBuilder(); double MM=304.8; var opt=new Options{DetailLevel=ViewDetailLevel.Fine};
Func<Element,Solid> solidOf=e=>{Solid acc=null; foreach(var go in e.get_Geometry(opt)){IEnumerable<GeometryObject> objs=go is GeometryInstance gi?gi.GetInstanceGeometry().Cast<GeometryObject>():new[]{go}; foreach(var o in objs){var s=o as Solid; if(s==null||s.Volume<=1e-9)continue; try{acc=acc==null?s:BooleanOperationsUtils.ExecuteBooleanOperation(acc,s,BooleanOperationsType.Union);}catch{if(acc==null)acc=s;}}} return acc;};
var rc=new List<Element>(); foreach(var c in new[]{BuiltInCategory.OST_Floors,BuiltInCategory.OST_Walls,BuiltInCategory.OST_StructuralFoundation}) rc.AddRange(new FilteredElementCollector(document).OfCategory(c).WhereElementIsNotElementType());
var rs=rc.Select(e=>new{e,s=solidOf(e)}).Where(x=>x.s!=null).ToList();
var ds=new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(d=>{var k=d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString();return k=="ПЛ1"||k=="ПЛ2";}).ToList();
var stat=new Dictionary<string,int>(); int bad=0;
foreach(var d in ds){var k=d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString();
 Solid body=null; double bv=0; foreach(var go in d.get_Geometry(opt)){var s=go as Solid; if(s==null)continue; var bb=s.GetBoundingBox(); var vv=(bb.Max-bb.Min); double vol=vv.X*vv.Y*vv.Z; if(s.Volume>0&&vol>bv&&true){} }
 // plate = solid with the largest planar face area
 PlanarFace pf=null; foreach(var go in d.get_Geometry(opt)){var s=go as Solid; if(s==null||s.Volume<=1e-9)continue; foreach(Face fc in s.Faces){var p=fc as PlanarFace; if(p!=null&&(pf==null||p.Area>pf.Area))pf=p;}}
 var n=pf.FaceNormal; var bbx=pf.GetBoundingBox(); var uv=new[]{new UV(bbx.Min.U+0.01,bbx.Min.V+0.01),new UV(bbx.Max.U-0.01,bbx.Min.V+0.01),new UV(bbx.Max.U-0.01,bbx.Max.V-0.01),new UV(bbx.Min.U+0.01,bbx.Max.V-0.01),new UV((bbx.Min.U+bbx.Max.U)/2,(bbx.Min.V+bbx.Max.V)/2)};
 int hit=0; string rcn=""; foreach(var q in uv){var pt=pf.Evaluate(q); bool h=false; foreach(var r in rs){ var ln=Line.CreateBound(pt-n*(1.5/MM),pt+n*(1.5/MM)); var res=r.s.IntersectWithCurve(ln,new SolidCurveIntersectionOptions()); if(res!=null&&res.SegmentCount>0){h=true;rcn=r.e.Id.Value+"";break;} } if(h)hit++; }
 var c0=pf.Origin; string key=k+" normal "+Math.Round(n.X)+","+Math.Round(n.Y)+","+Math.Round(n.Z)+" plateZ "+Math.Round(c0.Z*MM)+" areaMM2 "+Math.Round(pf.Area*MM*MM)+" cornersOnRC "+hit+"/5";
 if(!stat.ContainsKey(key))stat[key]=0; stat[key]++; if(hit<5){bad++; if(bad<=15)sb.AppendLine("OFF-FACE "+k+" "+d.Id.Value+" hit "+hit+"/5 @"+Math.Round(c0.X*MM)+","+Math.Round(c0.Y*MM)+","+Math.Round(c0.Z*MM));}
}
foreach(var kv in stat.OrderBy(x=>x.Key)) sb.AppendLine(kv.Key+" x"+kv.Value);
sb.AppendLine("off-face plates "+bad);
return sb.ToString();
}
static void Pad() {