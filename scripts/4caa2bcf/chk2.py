import sys, subprocess, batch_util as bu, gx
slots = [int(a) for a in sys.argv[1:]]
bu.restart()
for k in slots:
    r = subprocess.run([sys.executable, '-X', 'utf8', 'chk.py', str(k)], capture_output=True, text=True, encoding='utf-8', cwd=gx.S)
    print('slot', k, r.stdout[-2500:], r.stderr[-800:])
    SX = 172179 + 31500 * k
    subprocess.run([sys.executable, '-X', 'utf8', 'pv.py', 'snap', 'r%d' % k, str(SX), '455939', str(SX + 31500), '470789', 'ISO без полей A1 (841.00 x 594.00 мм)', '110'], capture_output=True, cwd=gx.S)
bu.kill()
