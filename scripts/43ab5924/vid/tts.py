import asyncio, edge_tts, subprocess, re, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from scenes import SCENES
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.join(os.path.dirname(__file__), "audio"); os.makedirs(D, exist_ok=True)

async def one(sid, text):
    c = edge_tts.Communicate(text, "kk-KZ-DauletNeural", rate="-4%")
    await c.save(os.path.join(D, sid + ".mp3"))

def dur(p):
    r = subprocess.run([FF, "-i", p], capture_output=True, text=True, errors="ignore")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])

async def main():
    for s in SCENES: await one(s[0], s[1])
asyncio.run(main())
out = {s[0]: dur(os.path.join(D, s[0] + ".mp3")) for s in SCENES}
json.dump(out, open(os.path.join(D, "dur.json"), "w"), indent=1)
print(out, sum(out.values()))

