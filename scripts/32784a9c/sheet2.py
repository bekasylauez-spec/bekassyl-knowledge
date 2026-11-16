import fitz, glob, os, sys
from PIL import Image, ImageDraw
d = sys.argv[1]; out = sys.argv[2]
fs = sorted(glob.glob(os.path.join(d, '*.pdf')))
ims = []
for f in fs:
    p = fitz.open(f)[0]
    pix = p.get_pixmap(dpi=36)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    # frame: find bbox of non-white pixels
    g = im.convert('L').point(lambda v: 0 if v > 200 else 255)
    bb = g.getbbox()
    w_mm, h_mm = p.rect.width/72*25.4, p.rect.height/72*25.4
    k = pix.width / w_mm
    print(os.path.basename(f), round(w_mm), 'x', round(h_mm), 'ink bbox mm L,T,R,B margins:', [round(bb[0]/k,1), round(bb[1]/k,1), round(w_mm-bb[2]/k,1), round(h_mm-bb[3]/k,1)])
    ims.append((os.path.basename(f), im))
W = 5; cw = 240; chh = 240
H = (len(ims)+W-1)//W
S = Image.new('RGB', (W*cw, H*(chh+16)), 'white'); dr = ImageDraw.Draw(S)
for i, (n, im) in enumerate(ims):
    im.thumbnail((cw-6, chh-6)); x, y = (i%W)*cw, (i//W)*(chh+16)
    S.paste(im, (x+3, y+16)); dr.text((x+3, y+2), n, fill='red'); dr.rectangle([x+3, y+16, x+3+im.width, y+16+im.height], outline='red')
S.save(out)
