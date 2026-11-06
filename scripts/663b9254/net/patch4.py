# Ведомость деталей: rows follow hoop_rows + sk_rows; extra rows = cloned template cell blocks + cloned row content.
s = open('gen3.py', encoding='utf-8').read()
a = s.index("V = {'1117B8'")
b_ = s.index("for h_, v in V.items(): add(t='settext', h=T(h_), s='%d' % v)")
b_ = b_ + len("for h_, v in V.items(): add(t='settext', h=T(h_), s='%d' % v)")
s = s[:a] + "pass\n" + s[b_:]
anchor = "TAB = dict("
NEW = r'''
# ---- Ведомость деталей ----
ROWC = {  # template rows: label, texts (top, left, right, bottom), sketch pline, 'по в.г.', 'L=', L value  (raw template handles)
    'X1': dict(lab='18DCB', top='18DD6', left='18DCE', right='18DD0', bot='18DCD', pl='18DE5', L='18DDC', rest=['18DE6', '18DCF']),
    'X2': dict(lab='18DCC', top='18DF1', left='18DE9', right='18DEB', bot='18DE8', pl='18E00', L='18DF7', rest=['18E01', '18DEA']),
    'S1': dict(lab='18DAF', top='18D9F', left='18D9E', bot='18DA2', pl='18DB0', ml='18DB3', L='18DA7', rest=['18DA1', '18DB1']),
    'S2': dict(lab='18DC5', top='18DB5', left='18DB4', bot='18DB8', pl='18DC6', ml='18DC9', L='18DBD', rest=['18DB7', '18DC7']),
}
def rowobjs(r): return [v for k, v in r.items() if k != 'rest'] + r['rest']
hx = max(len(hoop_rows) - 2, 0); skx = max(len(sk_rows) - 2, 0)
VX = 16550.0; VW = 3150.0
# 1) Ск rows move down by the extra hoop rows (before exploding the cell grid)
if hx: add(t='movegrp', h=[R_(x) for x in rowobjs(ROWC['S1']) + rowobjs(ROWC['S2'])], d=[0, -1000.0 * hx])
# 2) extra cells: explode the grid block, clone the last cell downwards
if hx + skx:
    add(t='explode', h=R_('18D95'), pre=PRE + 'VD')
    for k in range(1, hx + skx + 1):
        add(t='clone', h=PRE + 'VD15', base=[0, 0], to=[0, -1000.0 * k])
# 3) row content: hoop rows 0..len-1 (row 1 template = X2 content), Ск rows after them
def clone_row(src, dy, tagp):
    out = {}
    for k, v in src.items():
        if k == 'rest':
            out['rest'] = []
            for j, x in enumerate(v):
                add(t='clone', h=R_(x), base=[0, 0], to=[0, dy], tag=tagp + 'r%d' % j); out['rest'].append(tagp + 'r%d' % j)
        else:
            add(t='clone', h=R_(v), base=[0, 0], to=[0, dy], tag=tagp + k); out[k] = tagp + k
    return out
def raw(r): return {k: ([R_(x) for x in v] if k == 'rest' else R_(v)) for k, v in r.items()}
rows_h = [raw(ROWC['X1']), raw(ROWC['X2'])]
for k in range(2, len(hoop_rows)): rows_h.append(clone_row(ROWC['X2'], -1000.0 * (k - 1), PRE + 'VH%d' % k))
rows_s = [raw(ROWC['S1']), raw(ROWC['S2'])]
for k in range(2, len(sk_rows)):
    src = {kk: (vv if kk != 'rest' else vv) for kk, vv in ROWC['S2'].items()}
    rows_s.append(clone_row(src, -1000.0 * (hx + k - 1), PRE + 'VS%d' % k))
def st(hd, v): add(t='settext', h=hd, s=v)
# hoop rows
lab0 = rows_h[0]
st(lab0['top'], '%d' % (envb + 100)); st(lab0['bot'], '%d' % envb); st(lab0['left'], '%d' % envh); st(lab0['right'], '%d' % (envh + 100)); st(lab0['L'], 'L=%d' % X1L if False else '%d' % X1L)
for k, (labr, Lr, q) in enumerate(hoop_rows[1:], start=1):
    r = rows_h[k]
    st(r['lab'], labr)
    st(r['L'], '%d' % Lr)
    if labr == 'Х2':
        st(r['top'], '%d' % (dia + 100)); st(r['left'], '%d' % dia); st(r['right'], '%d' % (dia + 100)); st(r['bot'], '%d' % dia)
    else:   # S-pin: the template pin block (as in the sections) replaces the hoop sketch
        span = Lr - 200
        for kk in ('left', 'right', 'bot'): st(r[kk], '')
        st(r['top'], '%d' % span)
        yc = 18327.0 - 1000.0 * (k - 1)
        add(t='erase', h=[r['pl']])
        tg = PRE + 'VPIN%d' % k
        add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 40000, SY], to=W(17998, yc), tag=tg)
        add(t='dyn', h=tg, prop='Расстояние1', value=700)
for k in range(len(hoop_rows), 2): pass
# Ск rows (П-elements Ø16): width text + legs + L
for k, (labr, Lr, q) in enumerate(sk_rows):
    r = rows_s[k]
    st(r['lab'], labr); st(r['top'], '%d' % LEG); st(r['bot'], '%d' % LEG); st(r['left'], '%d' % (Lr - 2 * LEG)); st(r['L'], '%d' % Lr)
SKLAB = ';'.join(x[0] for x in sk_rows) if len(sk_rows) <= 2 else '%s...%s' % (sk_rows[0][0], sk_rows[-1][0])
add(t='mcset', h=T('111912'), set={'FirstLine': SKLAB}); add(t='mcset', h=T('11190F'), set={'FirstLine': SKLAB})
'''
s = s.replace(anchor, NEW + anchor, 1)
# the old 'if NPIN:' clearing of X2 sketch texts is superseded
s = s.replace("""if NPIN:
    add(t='settext', h=T('1117D3'), s=''); add(t='settext', h=T('1117CD'), s=''); add(t='settext', h=T('1117CA'), s='')
""", "")
open('gen3.py', 'w', encoding='utf-8').write(s)
print('ok')
