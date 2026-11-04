import fitz, sys, json, collections, os
f = sys.argv[1]; tag = sys.argv[2]; out = os.path.dirname(os.path.abspath(__file__))
d = fitz.open(f); MM = 25.4/72
res = []
for pn, p in enumerate(d):
    W, H = p.rect.width*MM, p.rect.height*MM
    spans = []
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            dirx, diry = l['dir']
            for s in l['spans']:
                t = s['text'].strip()
                if t: spans.append(dict(t=t, h=round(s['size']*MM, 2), x=round(s['origin'][0]*MM, 1), y=round(s['origin'][1]*MM, 1), font=s['font'], dir=[round(dirx,2), round(diry,2)], c=s['color']))
    lw = collections.Counter(); col = collections.Counter(); dash = collections.Counter(); fills = collections.Counter()
    for dr in p.get_drawings():
        w = dr.get('width') or 0
        n = len(dr['items'])
        lw[round(w*MM, 2)] += n
        col[str(dr.get('color'))] += n
        dash[str(dr.get('dashes'))] += n
        if dr.get('fill') is not None: fills[str(dr.get('fill'))] += n
    res.append(dict(page=pn+1, W=round(W), H=round(H), spans=spans, lw=lw.most_common(), col=col.most_common(8), dash=dash.most_common(8), fills=fills.most_common(5)))
    pix = p.get_pixmap(dpi=110); pix.save(os.path.join(out, '%s_p%02d.png' % (tag, pn+1)))
json.dump(res, open(os.path.join(out, tag + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
for r in res:
    hs = collections.Counter(s['h'] for s in r['spans'])
    print(tag, r['page'], r['W'], 'x', r['H'], 'spans', len(r['spans']), 'text h:', hs.most_common(8))
    print('   lw:', r['lw'][:10]); print('   dash:', r['dash'][:4])
