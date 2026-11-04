import fitz, glob, sys
pre = sys.argv[1]; dpi = int(sys.argv[2])
fs = sorted(glob.glob('pl/%s*.pdf' % pre))
for f in fs:
    fitz.open(f)[0].get_pixmap(dpi=dpi).save(f[:-4] + '.png')
print(len(fs), "png")
