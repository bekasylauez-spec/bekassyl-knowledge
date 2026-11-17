# -*- coding: utf-8 -*-
"""Мәтіннен кілт сөздерді контекстімен шығару. python -I kw.py file.txt ctx kw1 kw2 ..."""
import sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
path, ctx = sys.argv[1], int(sys.argv[2])
kws = sys.argv[3:]
lines = open(path, encoding="utf-8").read().split("\n")
for kw in kws:
    print("\n=================== [%s]" % kw)
    rx = re.compile(kw, re.I)
    n = 0
    for i, ln in enumerate(lines, 1):
        last_end = -1
        for m in rx.finditer(ln):
            if m.start() < last_end:
                continue
            a = max(0, m.start() - ctx)
            b = min(len(ln), m.end() + ctx)
            last_end = b
            n += 1
            print("L%d: %s%s%s" % (i, "…" if a > 0 else "", ln[a:b].strip(), "…" if b < len(ln) else ""))
    if n == 0:
        print("(табылмады)")
