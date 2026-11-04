import sys, os
BS = chr(92)
SP = sys.argv[1].replace('/', BS)
out = sys.argv[2]
names = {1: 'Общие данные', 2: 'Спецификация металлопроката', 3: 'Схема колонн', 4: 'Разрезы 1-1 2-2 3-3',
         5: 'Схема элементов по нижним поясам', 6: 'Схема элементов по верхним поясам', 7: 'Ферма ФФ1',
         8: 'Схема подкрановых конструкций', 9: 'Схема перекрытия', 10: 'Узлы 1 и 2', 11: 'Узлы 3-8'}
A1 = {3, 4, 5, 6, 8}
L = ['LOG|' + os.path.join(SP, 'out', 'merge.log')]
for k in range(1, 12):
    media = 'ISO_full_bleed_A1_(841.00_x_594.00_MM)' if k in A1 else 'ISO_full_bleed_A2_(594.00_x_420.00_MM)'
    L.append('SHEET|%s|%02d %s|%s|0|%d' % (os.path.join(SP, 'src0', 'L%d.dwg' % k), k, names[k], media, -100000 * k))
    if k == 1:
        L.append('PCOPY|15190|0|15550|350|-14979.8|56.5')
        L.append('PCOPY|5020|0|5200|40|-5000.9|10.2')
L.append('LOGO|' + os.path.join('D:' + BS, 'РАБОЧКА', 'От Шерхан', 'Завод', 'Том 14 Водоподготовка ВП-В109', 'КМ Чертеж', 'Company_logo.png') + '|21.0|12.04')
L.append('OUT|' + out)
open(os.path.join(SP, 'out', 'conf.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
