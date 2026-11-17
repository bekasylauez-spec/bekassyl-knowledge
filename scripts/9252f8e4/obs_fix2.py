import re
p = r'R:\Bekassyl\15_Проекты\Гостиница Касымова (Маке)\ЛИРА схема каркаса v1 (13.11.2026).md'
b = open(p, 'rb').read()
old = b'\r\n\r\r\n\r\n## v9 '
print('count', b.count(old))
f = b.replace(old, b'\r\n\r\n## v9 ', 1)
print('lone CR', [m.start() for m in re.finditer(rb'\r(?!\n)', f)], 'bare LF', len(re.findall(rb'(?<!\r)\n', f)))
open(p, 'wb').write(f)
