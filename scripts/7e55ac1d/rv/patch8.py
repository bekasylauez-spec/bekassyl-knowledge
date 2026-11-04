k = open('km2.cs', encoding='utf-8').read()
k3 = open('km3.cs', encoding='utf-8').read()


def rep(src, a, b, cnt=1):
    assert src.count(a) == cnt, (src.count(a), a[:90])
    return src.replace(a, b)


# new SPDS-style annotation families
k = rep(k, '''            RestyleFamilies(doc);''', '''            RestyleFamilies(doc);
            AnnoSet anno = MakeAnnoFamilies(doc, famDir);
            TagBeamSym = anno.TagBeam; TagColSym = anno.TagCol;''')
k = rep(k, '''            Dictionary<string, View> V = new Dictionary<string, View>();''', '''            ApplyAnno(doc, anno, vtSec, Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Detail), vtPlan);
            Dictionary<string, View> V = new Dictionary<string, View>();''')
# keep the КМ_Узел callout tag (drop the earlier switch to M_)
k = rep(k, '''                if (ct != null)
                    foreach (ViewFamilyType vft in new[] { vtDet, vtPlan, vtSec })''', '''                if (ct != null && anno.Callout == null)
                    foreach (ViewFamilyType vft in new[] { vtDet, vtPlan, vtSec })''')
# one type per mark, so the mark tags (label = type) read К1, ВП1 ...
k = rep(k, '''                    FamilyInstance fi = doc.Create.NewFamilyInstance(new XYZ(x, y, z1), csym[r[1]], lvBase, StructuralType.Column);''',
        '''                    FamilyInstance fi = doc.Create.NewFamilyInstance(new XYZ(x, y, z1), MarkType(doc, csym[r[1]], r[2]), lvBase, StructuralType.Column);''')
k = rep(k, '''                    FamilyInstance fi = doc.Create.NewFamilyInstance(Line.CreateBound(a, b), bs[r[1]], lvBase, brace ? StructuralType.Brace : StructuralType.Beam);''',
        '''                    FamilyInstance fi = doc.Create.NewFamilyInstance(Line.CreateBound(a, b), MarkType(doc, bs[r[1]], mk), lvBase, brace ? StructuralType.Brace : StructuralType.Beam);''')
k = rep(k, '''        static string BuildKM2(Application app, Dictionary<string, string> J)
        {''', '''        static FamilySymbol TagBeamSym, TagColSym;

        static FamilySymbol MarkType(Document doc, FamilySymbol baseSym, string mk)
        {
            FamilySymbol s = baseSym.Family.GetFamilySymbolIds().Select(id => (FamilySymbol)doc.GetElement(id)).FirstOrDefault(x => x.Name == mk);
            if (s == null) s = (FamilySymbol)baseSym.Duplicate(mk);
            if (!s.IsActive) s.Activate();
            return s;
        }

        static string BuildKM2(Application app, Dictionary<string, string> J)
        {''')
# plan marks: the new SPDS tags
k = rep(k, '''                FamilySymbol tagBeam = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault(s => s.FamilyName.StartsWith("M_Марка несущего каркаса"));
                FamilySymbol tagCol = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumnTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault();''',
        '''                FamilySymbol tagBeam = TagBeamSym, tagCol = TagColSym;''')
# fallback texts look like a shelf note (underlined)
k = rep(k, '''                                TextNote tn = Txt(doc, v.Id, head.X / MM, head.Y / MM, mk, t30, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);''',
        '''                                TextNote tn = Txt(doc, v.Id, head.X / MM, head.Y / MM, mk, t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                                FormattedText uf = tn.GetFormattedText(); uf.SetUnderlineStatus(true); tn.SetFormattedText(uf);''')
k = rep(k, '''                            if (ts != null)
                            {
                                IndependentTag tg = IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), col, TagOrientation.Horizontal, head);''',
        '''                            if (ts != null)
                            {
                                IndependentTag tg = IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), true, TagOrientation.Horizontal, head);''')
# levels in sections: short SPDS marks (the level line runs 20 mm past the stem, as in the DWG)
k = rep(k, '''                            XYZ pa = new XYZ(left.X, left.Y, lv.Elevation) + rd * (900 * MM), pb = new XYZ(right.X, right.Y, lv.Elevation) - rd * (300 * MM);''',
        '''                            XYZ pa = new XYZ(left.X, left.Y, lv.Elevation) + rd * (900 * MM), pb = pa + rd * (20 * MM * v.Scale);''')
open('km2.cs', 'w', encoding='utf-8').write(k)

# node marks: tags for members, underlined two-line notes for plates
k3 = rep(k3, '''                string txt = mk.StartsWith("-t") ? "-" + mk.Substring(1) + "\\rС245" : mk;
                try
                {
                    TextNoteOptions o = new TextNoteOptions(tt.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                    TextNote tn = TextNote.Create(doc, v.Id, head, txt, o);
                    Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = a;
                }''', '''                string txt = mk.StartsWith("-t") ? "-" + mk.Substring(1) + "\\rС245" : mk;
                try
                {
                    bool member = e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns;
                    FamilySymbol ts = e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns ? TagColSym : TagBeamSym;
                    if (member && ts != null)
                    {
                        IndependentTag tg = IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), true, TagOrientation.Horizontal, head);
                        if (tg.TagText == mk) continue;
                        doc.Delete(tg.Id);
                    }
                    TextNoteOptions o = new TextNoteOptions(tt.Id); o.HorizontalAlignment = HorizontalTextAlignment.Left; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                    TextNote tn = TextNote.Create(doc, v.Id, head, txt, o);
                    FormattedText ft = tn.GetFormattedText();
                    int n1 = txt.IndexOf('\\r'); ft.SetUnderlineStatus(new TextRange(0, n1 > 0 ? n1 : txt.Length), true);
                    tn.SetFormattedText(ft);
                    Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = a;
                }''')
open('km3.cs', 'w', encoding='utf-8').write(k3)
print('patched')
