import cv2, sys, os, glob, numpy as np
d = sys.argv[1]
fs = sorted(glob.glob(os.path.join(d, "v*_*.jpg")))
for s in range(0, len(fs), 8):
    tiles = []
    for f in fs[s:s+8]:
        im = cv2.resize(cv2.imread(f), (450, 800))
        cv2.putText(im, os.path.basename(f)[:-4], (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 2)
        tiles.append(im)
    while len(tiles) < 8: tiles.append(np.zeros((800,450,3), np.uint8))
    sheet = np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:])])
    cv2.imwrite(os.path.join(d, f"sheet_{s//8:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 82])
print(len(fs))
