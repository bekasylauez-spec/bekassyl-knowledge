import io
d = 'C:/Users/Admin/AppData/Local/Temp/claude/6aa9618bc913aab6/4ce2d6e1-1540-4a26-b399-75f1b59232ca/scratchpad/'
s = io.open(d + 'k100b2_sec5_v2.md', encoding='utf-8').read()
f = 'D:/РАБОЧКА/База_КМ/01_Объекты/Котельная 100 Гкал/КМ Блок 2/паспорт.md'
t = io.open(f, encoding='utf-8').read()
i = t.index('## 5. Узлы')
j = t.index('## 6. Спецификация')
io.open(f, 'w', encoding='utf-8', newline='\n').write(t[:i] + s + '\n' + t[j:])
print('ok')
