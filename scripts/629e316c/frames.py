import cv2, sys, os
out = sys.argv[1]
for tag, path in (("v1", sys.argv[2]), ("v2", sys.argv[3])):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(tag, "fps", fps, "frames", n, "dur", round(n/fps,1) if fps else 0, w, h)
    step = int(fps*2) if fps else 60
    i = 0; k = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok: break
        s = 900.0/max(fr.shape[:2])
        fr = cv2.resize(fr, None, fx=s, fy=s)
        cv2.imwrite(os.path.join(out, f"{tag}_{k:03d}.jpg"), fr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        k += 1; i += step
    print(tag, "saved", k)
