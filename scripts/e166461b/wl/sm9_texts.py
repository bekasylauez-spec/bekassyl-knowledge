# См-9 sheets 5.36/5.37: titles, sheet numbers, notes (sheet range, 61d), stamp name of 5.36; axis 2/1 (not in our scheme) removed.
import sys, ezdxf; sys.path.insert(0, 'wl'); from common import *
doc = ezdxf.readfile(gx.S + r'\w\kt.dxf'); E = {e.dxf.handle: e for e in doc.modelspace().query('TEXT MTEXT')}
txt = lambda h: E[h].text if E[h].dxftype() == 'MTEXT' else E[h].dxf.text
NAME = 'монолитной стены между осями 2 и 3 стена См-9 (тол.250мм)'
ops = [dict(t='settext', h='276DAB', s='{\LОпалубочный чертеж ' + NAME + '}'),
       dict(t='settext', h='277AAC', s='{\LВертикальное армирование ' + NAME + '}'),
       dict(t='settext', h='277AAF', s='{\LГоризонтальное армирование ' + NAME + '}'),
       dict(t='settext', h='277AA4', s=txt('277AA4').replace('Вертикальное,горизонтальное', 'Вертикальное, горизонтальное').replace('между осями 2/1 и 3 стена См-8', 'между осями 2 и 3 стена См-9')),
       dict(t='settext', h='276E4D', s='5.36'), dict(t='settext', h='277AA7', s='5.37')]
for h in ('276E4F', '277AA9'):
    ops.append(dict(t='settext', h=h, s=txt(h).replace('КЖ-4.30 ... 4.32', 'КЖ-5.36 ... 5.38').replace('71d', '61d')))
ops.append(dict(t='clone', h='277AA4', base=[2543100, 0], to=[2483700, 0], text=txt('277AA4').replace('Вертикальное,горизонтальное армирование', 'Опалубочный чертеж').replace('между осями 2/1 и 3 стена См-8', 'между осями 2 и 3 стена См-9')))
# axis 2/1: plan 1-1 (5.36) and section 1-1 (5.37); plan dims 625 / 125 / 125 -> wall thickness 250
ops += [dict(t='erase', h=['276DF9', '276FCE', '276DEA', '27819E']),
        dict(t='dimpts', h='276DDB', p1=[2483700 + 34910, 455939 + 27874], p2=[2483700 + 34910, 455939 + 28124], dl=[2483700 + 33163, 455939 + 27999]),
        dict(t='dimdef', h=['276DDB']), dict(t='save')]
for o in ops[:8]: print(o.get('s', '')[:200].replace('\n', ' '))
print(gx.run(ops, 's9t')[-200:])
