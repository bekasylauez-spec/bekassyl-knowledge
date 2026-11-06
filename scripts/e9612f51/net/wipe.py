import gx, sys
def wipe(P):
    m = gx.tagmap(); p = P.rstrip(':')
    hs = [k for k in m if k.startswith(P) or k.startswith(p + '_') or k.startswith(p + 'S')]
    return gx.run([dict(t='erase', h=hs)], 'wipe' + p), len(hs)
if __name__ == '__main__':
    o, n = wipe(sys.argv[1]); print(n, [l for l in o.splitlines() if 'done' in l])
