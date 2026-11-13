import sys, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = open(sys.argv[1], "w", encoding="utf-8")
P = {
 "kk": "Өрт лестницасын өлшеп жатырмыз. Мына жерге дейін алты метр, мына стенамен екі жетпіс, этаж биіктігі үш метр жиырма, площадканың ені бір метр жиырма, ұзындығы екі отыз бес, ступень отыз, сексен, тоқсан, жүз жиырма сантиметр.",
 "ru": "Замеряем пожарную лестницу. До этого места шесть метров, по стене два семьдесят, высота этажа три двадцать, площадка метр двадцать, длина два тридцать пять, ступень тридцать, восемьдесят, девяносто сантиметров.",
}
for f in sys.argv[2:]:
    w = wave.open(f, "rb")
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    for lang in ("kk", "ru"):
        segs, info = m.transcribe(a, language=lang, beam_size=8, best_of=8, vad_filter=False,
                                  initial_prompt=P[lang], condition_on_previous_text=False,
                                  temperature=[0.0, 0.2, 0.4], no_speech_threshold=0.8, word_timestamps=False)
        out.write(f"===== {f[-7:]} {lang}\n")
        for s in segs:
            out.write(f"[{s.start:6.1f}-{s.end:6.1f}] ({s.avg_logprob:.2f}) {s.text.strip()}\n")
        out.flush()
out.close()
