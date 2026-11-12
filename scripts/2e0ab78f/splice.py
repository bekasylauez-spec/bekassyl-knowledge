import os
os.chdir(r'D:\_claude_work\otst\s1')
p = 's1_p3.py'; s = open(p, encoding='utf-8').read()
a = s.index('def b32():'); b = s.index('def b35():')
new = open(r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\2e0ab78f-f731-49e4-9b7c-ac59ff6a470a\scratchpad\new_b32_b33.py', encoding='utf-8').read()
s = s[:a] + new + s[b:]
s = s.replace('from s1_p34 import NOTES\n', 'from s1_p34 import NOTES, DET_FM1\n')
s = s.replace('"""3.2 осн. арматура Фм-1 (план, узел стыковки); 3.3 фрагменттер (арм.), Кр-1;', '"""3.2 осн. арматура Фм-1 (план, разрез 1-1, приямок, выпуски Км-1, узел стыковки); 3.3 разрез 2-2, ведомость деталей, Кр-1;')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
