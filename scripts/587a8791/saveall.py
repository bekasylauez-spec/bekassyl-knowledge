import os, sys, importlib
sys.path.insert(0, r'D:\_claude_work\tsekh'); os.chdir(r'D:\_claude_work\tsekh')
sys.stdout.reconfigure(encoding='utf-8')
for ch, doc in (('', '9. Лестница Цех предобработки.dwg'), ('6', '1. Общие данные Цех предобработки.dwg'), ('7', '7. Плиты Цех предобработки.dwg')):
    os.environ['TSCH'] = ch
    import ab; ab = importlib.reload(ab); ab.DOC = doc
    ops = [{'t': 'sysvar', 'n': n, 'v': 1} for n in ('FILEDIA', 'CMDDIA', 'SECURELOAD')] + [{'t': 'save'}]
    o = ab.run(ops, 'svall', 180)
    print(repr(ch), doc, o[o.find('done'):][:30].strip())
