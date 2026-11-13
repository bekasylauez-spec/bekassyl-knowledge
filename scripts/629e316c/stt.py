import sys, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = open(sys.argv[1], "w", encoding="utf-8")
for f in sys.argv[2:]:
    w = wave.open(f, "rb")
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    for lang in ("kk", "ru"):
        segs, info = m.transcribe(a, language=lang, beam_size=5, vad_filter=True)
        out.write(f"===== {f[-6:]} {lang}\n")
        for s in segs:
            out.write(f"[{s.start:6.1f}-{s.end:6.1f}] {s.text.strip()}\n")
        out.flush()
out.close()
