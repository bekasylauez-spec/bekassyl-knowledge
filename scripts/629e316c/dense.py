import cv2, sys, os, numpy as np
out, path = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(path)
def sheet(name, times):
    tiles=[]
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t*1000); ok, fr = cap.read()
        if not ok: fr = np.zeros((1024,576,3),np.uint8)
        fr = cv2.resize(fr,(506,900))
        cv2.putText(fr, f"{t:.1f}s", (8,30), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(0,255,255),2)
        tiles.append(fr)
    cv2.imwrite(os.path.join(out,name), np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY,85])
sheet("d1.jpg",[33,34,35,36])
sheet("d2.jpg",[37,38,39,40])
sheet("d3.jpg",[41,42,43,44])
sheet("d4.jpg",[45,46,47,48.5])
