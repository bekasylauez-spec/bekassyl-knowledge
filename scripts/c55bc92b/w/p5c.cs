// probe: node 2 4-D weld A#0 (kf8 along x) vs B#0 (vertical kf6): direct difference / intersect behaviour
var d = document; var sb = new StringBuilder();
var A = QSolidsOf(d.GetElement(new ElementId(2895765L))); var B = QSolidsOf(d.GetElement(new ElementId(2895766L)));
var a = A[0]; var b = B[0];
sb.AppendLine("A vol " + QF(QCu(a.Volume)) + " B vol " + QF(QCu(b.Volume)));
try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); sb.AppendLine("intersect(A,B) direct = " + QF(r == null ? 0 : QCu(r.Volume))); } catch (Exception ex) { sb.AppendLine("intersect(A,B) FAIL " + ex.Message.Split('\n')[0]); }
try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(b, a, BooleanOperationsType.Intersect); sb.AppendLine("intersect(B,A) direct = " + QF(r == null ? 0 : QCu(r.Volume))); } catch (Exception ex) { sb.AppendLine("intersect(B,A) FAIL " + ex.Message.Split('\n')[0]); }
try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(b, a, BooleanOperationsType.Difference); sb.AppendLine("diff(B-A) = " + QF(r == null ? 0 : QCu(r.Volume)) + " (B " + QF(QCu(b.Volume)) + ")"); } catch (Exception ex) { sb.AppendLine("diff(B-A) FAIL " + ex.Message.Split('\n')[0]); }
bool vs, fl; double v1 = QOvlVol(a, b, out vs, out fl); sb.AppendLine("QOvlVol(A,B) " + QF(v1) + " vs " + vs + " fl " + fl);
double v2 = QOvlVol(b, a, out vs, out fl); sb.AppendLine("QOvlVol(B,A) " + QF(v2) + " vs " + vs + " fl " + fl);
// planes of A faces
foreach (Face f in a.Faces) { var pf = f as PlanarFace; if (pf != null) sb.AppendLine("A face n=" + QF(pf.FaceNormal.X) + "," + QF(pf.FaceNormal.Y) + "," + QF(pf.FaceNormal.Z) + " d=" + QF(pf.FaceNormal.DotProduct(pf.Origin) / QMM) + " area " + QF(pf.Area / (QMM * QMM))); }
foreach (Face f in b.Faces) { var pf = f as PlanarFace; if (pf != null) sb.AppendLine("B face n=" + QF(pf.FaceNormal.X) + "," + QF(pf.FaceNormal.Y) + "," + QF(pf.FaceNormal.Z) + " d=" + QF(pf.FaceNormal.DotProduct(pf.Origin) / QMM) + " area " + QF(pf.Area / (QMM * QMM))); }
return sb.ToString();
}
