import sys, glob, os
sys.stdout.reconfigure(encoding="utf-8")
from faster_whisper import WhisperModel

files = sorted(glob.glob(os.path.expanduser(r"~\Downloads\WhatsApp Ptt 2026-10-26 at 16.17.*.ogg")))
model = WhisperModel(sys.argv[1] if len(sys.argv) > 1 else "medium", device="cpu", compute_type="int8")
import av, numpy as np


def load(path):
    with av.open(path) as c:
        rs = av.AudioResampler(format="s16", layout="mono", rate=16000)
        chunks = [r.to_ndarray().reshape(-1) for fr in c.decode(audio=0) for r in rs.resample(fr)]
        chunks += [r.to_ndarray().reshape(-1) for r in rs.resample(None)]
    return np.concatenate(chunks).astype(np.float32) / 32768.0


out = []
for f in files:
    audio = load(f)
    for lang in ("kk",):
        segs, info = model.transcribe(audio, language=lang, beam_size=5)
        text = " ".join(s.text.strip() for s in segs)
        out.append(f"=== {os.path.basename(f)} [{lang}] ===\n{text}\n")
        print(out[-1], flush=True)
open(os.path.join(os.path.dirname(__file__), "transcript.txt"), "w", encoding="utf-8").write("\n".join(out))
