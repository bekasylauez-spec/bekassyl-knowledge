import glob, re, io
import zstandard as z

BS = chr(92)
for f in sorted(glob.glob(r'C:/Users/Admin/.codex/sessions/2026/09/2[6-9]/*.zst')):
    d = z.ZstdDecompressor().stream_reader(open(f, 'rb'))
    t = io.TextIOWrapper(d, encoding='utf-8', errors='ignore').read()
    t = t.replace(BS * 2, BS)
    hits = set(re.findall(r'[A-Za-z]:\\[^"\n\\<>|*?]+(?:\\[^"\n\\<>|*?]+)*\.(?:rvt|dwg|pdf|xlsx|csv|py|dyn|md|json|ifc|txt|zip)', t))
    print('==', f, len(t), 'FRAME_20260927' in t)
    for h in sorted(hits):
        if re.search(r'(?i)onko|онко|frame|revit|codex', h):
            print('  ', h)
