p='rmc_n_lib.cs'; s=open(p,encoding='utf-8').read(); part=open(r'C:/Users/Admin/AppData/Local/Temp/claude/a7137524bdaa49d0/c55bc92b-0511-4932-9c00-c1294111057c/scratchpad/part2.cs',encoding='utf-8').read()
assert '//@@PART2@@' in s
s=s.replace('//@@PART2@@\n',part); open(p,'w',encoding='utf-8').write(s)
