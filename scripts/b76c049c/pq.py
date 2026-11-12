import sys, os, subprocess, shutil
sys.path.insert(0, r"D:\_claude_work\otst\s4")
import s4_ab
# usage: pq.py name X0 [W H]  -> name.png (130 dpi, s4 folder) + scratch name_q1..q4 (190 dpi)
n = sys.argv[1]; X0 = float(sys.argv[2]); Y0 = -300000.0; W, H = 29700.0, 21000.0
S = r"D:\_claude_work\otst\s4"; SC = os.path.dirname(os.path.abspath(__file__))
print(s4_ab.run([dict(t="save")], "save")[:60])
shutil.copy(os.path.join(S, "КЖ Третичный отстойник D10.dwg"), os.path.join(S, "s4_plot.dwg"))
PW = r"D:\_claude_work\otst\tools\plotwin.py"
env = dict(os.environ, OUT=S, DPI="130")
print(subprocess.run([sys.executable, PW, os.path.join(S, "s4_plot.dwg"), n, str(X0), str(Y0), str(X0 + W), str(Y0 + H)], env=env, capture_output=True, text=True).stdout)
if len(sys.argv) < 4 or sys.argv[3] != 'noq':
    env = dict(os.environ, OUT=SC, DPI="190")
    a = []
    for i, (qx, qy) in enumerate(((0, 1), (1, 1), (0, 0), (1, 0))):
        a += [n + "_q%d" % (i + 1), str(X0 + qx * W / 2), str(Y0 + qy * H / 2), str(X0 + (qx + 1) * W / 2), str(Y0 + (qy + 1) * H / 2)]
    print(subprocess.run([sys.executable, PW, os.path.join(S, "s4_plot.dwg")] + a, env=env, capture_output=True, text=True).stdout)
