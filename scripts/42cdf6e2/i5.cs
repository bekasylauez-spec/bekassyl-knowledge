var sb=new System.Text.StringBuilder(); double MM=304.8;
var fr=new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
var ds=new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().Select(d=>new{d,k=d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString(),bb=d.get_BoundingBox(null)}).ToList();
int noPl=0,noCap=0,endsFree=0; var vb=new Dictionary<string,int>();
foreach(var f in fr){var c=((LocationCurve)f.Location).Curve; var u=(c.GetEndPoint(1)-c.GetEndPoint(0)).Normalize(); string nm=f.Symbol.Name; var hb=(f.Symbol.LookupParameter("b").AsDouble())/2;
 for(int e=0;e<2;e++){var P=c.GetEndPoint(e); var o=e==0?-u:u; double ext=f.get_Parameter(e==0?BuiltInParameter.START_EXTENSION:BuiltInParameter.END_EXTENSION).AsDouble(); var E=P+o*ext;
  bool other=fr.Any(g=>g!=f&&((LocationCurve)g.Location).Curve.Distance(P)<1.0/MM);
  if(other)continue; endsFree++;
  Func<string,bool> has=mk=>ds.Any(x=>x.k==mk&&x.bb!=null&&new Outline(x.bb.Min-new XYZ(0.03,0.03,0.03),x.bb.Max+new XYZ(0.03,0.03,0.03)).Contains(E+o*(0.002),0.0)||x.k==mk&&x.bb!=null&&new Outline(x.bb.Min-new XYZ(0.03,0.03,0.03),x.bb.Max+new XYZ(0.03,0.03,0.03)).Contains(E,0.0));
  bool pl=has("ПЛ1")||has("ПЛ2"); bool cap=has("ПЛ3");
  if(!pl&&!cap){noCap++; if(noCap<=10)sb.AppendLine("FREE END no plate/cap "+f.Id.Value+" "+nm+" @"+Math.Round(E.X*MM)+","+Math.Round(E.Y*MM)+","+Math.Round(E.Z*MM));}
  if(pl&&cap){sb.AppendLine("BOTH plate and cap "+f.Id.Value+" "+nm);}
  if(nm!="Кр1"&&Math.Abs(u.Z)>0.99&&o.Z<0){var k=nm+" bottom z="+Math.Round(E.Z*MM)+" plate="+pl; if(!vb.ContainsKey(k))vb[k]=0; vb[k]++;}
 }}
sb.AppendLine("free ends "+endsFree+" without plate/cap "+noCap);
foreach(var kv in vb)sb.AppendLine(kv.Key+" x"+kv.Value);
// Kr1 count with plates
sb.AppendLine("Kr1 "+fr.Count(f=>f.Symbol.Name=="Кр1"));
return sb.ToString();
}
static void Pad() {