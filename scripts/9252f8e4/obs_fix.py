import re
p = r'R:\Bekassyl\15_Проекты\Гостиница Касымова (Маке)\ЛИРА схема каркаса v1 (13.11.2026).md'
b = open(p, 'rb').read()
lone = [m.start() for m in re.finditer(rb'\r(?!\n)', b)]
print('lone CR at', lone)
for i in lone:
    print(repr(b[max(0, i - 40):i + 20].decode('utf-8', 'replace')))
fixed = b.replace(b'\\Kasymova\res_v10', b'\\Kasymova\\res_v10')
print('replaced', b.count(b'\\Kasymova\res_v10'))
lone2 = [m.start() for m in re.finditer(rb'\r(?!\n)', fixed)]
print('lone CR after', lone2)
if fixed != b:
    open(p, 'wb').write(fixed)
t = fixed.decode('utf-8')
print(t[t.index('## v10 есебінің'):][:700])
