import sys, os, time
sys.path.insert(0, r"D:\РАБОЧКА\.claude\shutdown_watch")
import sessions_idle_wait as w
proj = r"C:\Users\Admin\.claude\projects\D---------"
now = time.time()
for sid in ("94c03bfb-48e3-4972-8913-5871021722f0", "3e50b09e-f733-4310-9158-fc456184a213", "e16b7880-ce7d-4c61-8df7-b1c1a87009ed", "10893214-c5f6-4902-9f78-d792a6f31f71"):
    data, tr = w.read_tail(os.path.join(proj, sid + ".jsonl"), 3 * 1024 * 1024)
    print(sid[:8], "pending/persistent:", w.pending_bg(sid, proj, data, now, 3 * 1024 * 1024, 12.0, 60.0, 3.0))