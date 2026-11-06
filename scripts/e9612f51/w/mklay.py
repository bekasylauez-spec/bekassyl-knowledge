import os, json, sys, time, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'net'))
import gx
W = gx.S + r'\w'; T = os.environ['TEMP']
lines = []
for k in range(1, 31):
    B = json.load(open(W + r'\sh_%d.json' % k, encoding='utf-8'))
    x0 = 172179 + 31500 * (k - 1)
    lines.append('%s|%d|%d|%d|%d|50' % (B['no'], x0, 455939, x0 + 31500, 470789))
open(T + r'\lay3.txt', 'w', encoding='utf-8').write('\n'.join(lines))
if '--pdf' in sys.argv: open(T + r'\lay3_pdf.txt', 'w', encoding='utf-8').write(W + r'\pdf')
elif os.path.exists(T + r'\lay3_pdf.txt'): os.remove(T + r'\lay3_pdf.txt')
jd = T + r'\acadjob_b3'
try: os.remove(jd + r'\done.txt')
except OSError: pass
open(jd + r'\job.txt', 'w', encoding='utf-8').write(gx.S + r'\net\lay3c.dll|LAY3.Cmds|Apply|b3w.dwg')
t0 = time.time()
while time.time() - t0 < 1800 and not os.path.exists(jd + r'\done.txt'): time.sleep(2)
print(open(jd + r'\done.txt', encoding='utf-8').read()[:300] if os.path.exists(jd + r'\done.txt') else 'timeout')
print(open(T + r'\lay3_log.txt', encoding='utf-8-sig').read()[-1500:] if os.path.exists(T + r'\lay3_log.txt') else '')
