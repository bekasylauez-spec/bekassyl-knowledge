import json, ezdxf
json.dump([{'t': 'stretchWin', 'w': [1320000, -815000, 1344680, -807500], 'ycut': -810600, 'dy': 700, 'keep': ['642D7E']}],
          open('fx_s28.json', 'w', encoding='utf-8'))
doc = ezdxf.readfile('p5.dxf')
n = doc.entitydb['6A3049'].text.replace('^I', '\t').replace('^J', '\\P').replace('^ ', '^')
assert 'листом КЖ-2.8' in n
n = n.replace('листом КЖ-2.8', 'листом КЖ-2.6')
SRC = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\fx\p5.dwg'
ops = [{'t': 'import', 'src': SRC, 'w': [2693480, -989730, 2735500, -960015], 'd': [-754800, 0], 'tag': 'pm6'},
       {'t': 'text', 'h': '@5E7A40', 'v': '\\pxqc;{\\C0;Опалубочный чертеж плиты покрытия Пм-6 на отм. +21.500}'},
       {'t': 'text', 'h': '@5E7D47', 'v': '\\pxqc;{\\C0;Схема расположения основной арматуры плиты покрытия Пм-6 на отм. +21.500}'},
       {'t': 'text', 'h': '@696019', 'v': 'Опалубочный чертеж и армирование плиты покрытия Пм-6 на отм. +21.500'},
       {'t': 'text', 'h': '@6842EC', 'v': '7.39'},
       {'t': 'text', 'h': '@6A3049', 'v': n},
       {'t': 'cells', 'h': '@5F8C63', 'nolayout': 1, 'cells': [[0, 2, 'Плита Пм-6']]},
       {'t': 'cells', 'h': '@5F928E', 'nolayout': 1, 'cells': [[6, 0, 'Плита Пм-6']]}]
json.dump(ops, open('fx_pm6.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok')
