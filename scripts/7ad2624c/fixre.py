p = r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_hide_node_marks.cs'
s = open(p, encoding='utf-8').read()
s = s.replace('(\\d)-' + chr(1) + '$', '(\\d)-\\1$')
open(p, 'w', encoding='utf-8').write(s)
print(chr(1) in s, '(\\d)-\\1$' in s)
