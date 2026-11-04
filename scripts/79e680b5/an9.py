import ezdxf, sys
doc = ezdxf.readfile(sys.argv[1])
e = doc.entitydb['1285A9']
t = e.text
i = t.find('34028-2016.  ')
print(t[i:i+400])
print('plain:', e.plain_text()[e.plain_text().find('Каменная'):][:160])
for h in ['1285AB']:
    x = doc.entitydb[h].text
    j = x.find('Площадь')
    print(h, x[j:j+120])
