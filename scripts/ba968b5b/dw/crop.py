import fitz, sys
d = fitz.open('w/album_new.pdf')
for i, p in enumerate(d):
    dr = p.get_drawings()
    big = max(dr, key=lambda g: g['rect'].width * g['rect'].height)['rect']
    U = fitz.Rect()
    for g in dr: U |= g['rect']
    r = fitz.Rect(min(U.x0, big.x0) - 1.5, big.y0 - 1.5, big.x1 + 1.5, max(U.y1, big.y1) + 1.5)
    # «Формат А2» жазуы рамка астында — қиып тастамау
    for b in p.get_text('blocks'):
        br = fitz.Rect(b[:4])
        if br.y0 >= big.y1 - 2 and br.x0 >= big.x0 and br.x1 <= big.x1 + 2 and br.y0 < big.y1 + 30:
            r.y1 = max(r.y1, br.y1 + 1)
    H = p.mediabox.height
    p.set_mediabox(fitz.Rect(r.x0, H - r.y1, r.x1, H - r.y0))
d.save('w/album_crop.pdf', garbage=3, deflate=True)
for i in (0, 2, 6, 17, 26, 38):
    q = fitz.open('w/album_crop.pdf')[i]; print(i, q.rect, q.mediabox)
    q.get_pixmap(dpi=30).save('w/crop_%d.png' % i)
