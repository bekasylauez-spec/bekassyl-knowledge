import ab
print(ab.run([{'t':'extdump','file':ab.S+r'\w\ext.txt'}],'ex')[-100:])
o=ab.run([{'t':'notelist'}],'nl'); open(ab.S+r'\w\notes.txt','w',encoding='utf-8').write(o); print(len(o))
