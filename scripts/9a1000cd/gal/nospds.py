import gx, os, time, collections, sys
TMP = os.environ['TEMP']
def count():
    gx.run([dict(t='list', win=[-1e7, -1e7, 1e7, 1e7])], 'nsl', doc='nospds.dwg', wait=600)
    c = collections.Counter(l.split('\t')[1] for l in open(os.path.join(TMP, 'm2_log.txt'), encoding='utf-8-sig') if l[:2] in ('L\t', 'N\t'))
    return sum(v for k, v in c.items() if k.upper().startswith(('SPDS', 'MCS'))), c
n, c = count(); print('before SPDS', n, sum(c.values()))
if 'count' in sys.argv: sys.exit()
s = '(setvar "QAFLAGS" 1)(setq ss (ssget "_X" (list (cons 0 "SPDS*,MCS*") (cons 410 "Model"))))(if ss (command "_.EXPLODE" ss ""))(setvar "QAFLAGS" 0)(princ) \n'
print(gx.run([dict(t='cmd', s=s)], 'nsx', doc='nospds.dwg')[-200:])
for i in range(40):
    time.sleep(15)
    try:
        n, c = count(); print('after', i, 'SPDS', n, sum(c.values()), flush=True)
        if n == 0: break
    except gx.Hang: print('busy', i, flush=True)
