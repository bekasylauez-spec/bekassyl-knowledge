import sys, gx, fitz
SX = float(sys.argv[1]); name = sys.argv[2]; W_ = float(sys.argv[3]) if len(sys.argv) > 3 else 29700; H_ = float(sys.argv[4]) if len(sys.argv) > 4 else 21000
f = gx.S + r'\png\%s.pdf' % name
media = 'ISO_full_bleed_A2_(594.00_x_420.00_MM)' if W_ < 40000 else 'ISO_full_bleed_A1_(841.00_x_594.00_MM)'
gx.run([{'t': 'plotpdf', 'win': [SX, 271898, SX + W_, 271898 + H_], 'file': f, 'media': media}], 'pl')
d = fitz.open(f); p = d[0]; r = p.rect
p.get_pixmap(dpi=110).save(gx.S + r'\png\%s.png' % name)
for i, (a, b) in enumerate(((0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5))):
    p.get_pixmap(dpi=190, clip=fitz.Rect(r.width * a, r.height * b, r.width * (a + 0.5), r.height * (b + 0.5))).save(gx.S + r'\png\%s_q%d.png' % (name, i))
print('ok', f)
