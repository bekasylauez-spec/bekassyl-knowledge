# -*- coding: utf-8 -*-
"""Проверка АБК.xlsx (v3: уровни -2.000, 0.000 Бф-1, +3.300, +6.600) — по аналогу «Проверка Онкологический цетр Б1 С1.xlsx» (те же листы и формулы).
Исходные числа: chk.json (CSV ЛИРА). Этажи: -2.000 (верх Фм-1), +3.300, +6.600 — уровни дисков перекрытий
(на 0.000 плиты нет — плита по грунту в расчетной схеме не моделируется)."""
import sys, json
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

d = json.load(open('chk.json', encoding='utf-8'))
out = sys.argv[1]
LV = ['-2.0', '0.0', '3.3', '6.6']; N = len(LV)   # 0.000 — уровень фундаментных балок Бф-1 (v3)
X, Y = d['dir13'], d['dir14']
W = {L: d['W'][L] for L in LV}
F = lambda b=False: Font(name='ISOCPEUR', size=11, bold=b, italic=True)
th = Side(style='thin'); BR = Border(left=th, right=th, top=th, bottom=th)
HL = PatternFill('solid', fgColor='FFF2CC')

wb = openpyxl.Workbook()
def sheet(name):
    ws = wb.create_sheet(name)
    for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': ws.column_dimensions[k].width = 13
    return ws
def put(ws, ref, v, b=False, fmt=None, wrap=False):
    c = ws[ref]; c.value = v; c.font = F(b); c.border = BR
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=wrap)
    if fmt: c.number_format = fmt
    return c
wb.remove(wb.active)

# ---------------- Регулярность в плане ----------------
ws = sheet('Регулярность в плане')
for col, t in zip('ABCDEOP', ['Отметка', 'Х max', 'Х min', 'У max', 'У min', 'Х сред', 'У сред']): put(ws, col + '1', t, True)
for i, L in enumerate(LV):
    r = 2 + i
    put(ws, 'A%d' % r, float(L), fmt='0.000')
    dx, dy = X['disp_dom'][L], Y['disp_dom'][L]
    for col, v in zip('BCDE', (dx['max'], dx['min'], dy['max'], dy['min'])): put(ws, '%s%d' % (col, r), round(v, 2), fmt='0.00')
    put(ws, 'O%d' % r, '=(B%d+C%d)/2' % (r, r), fmt='0.00'); put(ws, 'P%d' % r, '=(D%d+E%d)/2' % (r, r), fmt='0.00')
ws['G1'] = 'Перемещения, мм — по основным формам: X — форма %d, Y — форма %d (загружения 13, 14)' % (d['dom']['13'], d['dom']['14']); ws['G1'].font = F()
ws.merge_cells('A10:I10'); put(ws, 'A10', 'Таблица 1. Проверка регулярности здания в плане', True)
ws.merge_cells('B11:E11'); ws.merge_cells('F11:I11')
put(ws, 'A11', 'отметка', True); put(ws, 'B11', 'Форма %d SX' % d['dom']['13'], True); put(ws, 'F11', 'Форма %d SY' % d['dom']['14'], True)
for col, t in zip('BCDEFGHI', ['∆ min, мм', '∆ max, мм', '∆ ср, мм', 'условие Ж 3.2. б), %'] * 2): put(ws, col + '12', t, True, wrap=True)
rows = []
for i, L in enumerate(LV[1:]):
    r = 13 + i; s = 3 + i; rows.append(r)
    put(ws, 'A%d' % r, '=A%d' % s, fmt='0.000')
    put(ws, 'B%d' % r, '=C%d' % s, fmt='0.00'); put(ws, 'C%d' % r, '=B%d' % s, fmt='0.00')
    put(ws, 'D%d' % r, '=(B%d+C%d)/2' % (r, r), fmt='0.00'); put(ws, 'E%d' % r, '=100-((D%d/C%d)*100)' % (r, r), fmt='0.00')
    put(ws, 'F%d' % r, '=E%d' % s, fmt='0.00'); put(ws, 'G%d' % r, '=D%d' % s, fmt='0.00')
    put(ws, 'H%d' % r, '=(F%d+G%d)/2' % (r, r), fmt='0.00'); put(ws, 'I%d' % r, '=100-((H%d/G%d)*100)' % (r, r), fmt='0.00')
rm = rows[-1] + 1
put(ws, 'E%d' % rm, '=MAX(E%d:E%d)' % (rows[0], rows[-1]), True, '0.00'); put(ws, 'I%d' % rm, '=MAX(I%d:I%d)' % (rows[0], rows[-1]), True, '0.00')
for k, (t, f) in enumerate((('Регулярное в плане ', '<10'), ('Умеренно нерегулярное', '<25'), ('Чрезмерно нерегулярное ', '>25'))):
    r = rm + 1 + k
    put(ws, 'A%d' % r, t); put(ws, 'E%d' % r, '=IF(E%d%s,"ДА","НЕТ")' % (rm, f), True)
    put(ws, 'F%d' % r, t); put(ws, 'I%d' % r, '=IF(I%d%s,"ДА","НЕТ")' % (rm, f), True)
ws.column_dimensions['A'].width = 24

# ---------------- Регулярность по высоте ----------------
wh = sheet('Регулярность по высоте')
put(wh, 'A1', 'Средние', True); put(wh, 'B1', 'Х', True); put(wh, 'C1', 'У', True)
put(wh, 'E2', 'Масса', True); put(wh, 'F2', 'm, т', True); put(wh, 'H2', 'Сейсмика, т', True); put(wh, 'I2', 'Х', True); put(wh, 'J2', 'У', True)
for i, L in enumerate(LV):
    r = 2 + i
    put(wh, 'A%d' % r, "='Регулярность в плане'!A%d" % r, fmt='0.000')
    put(wh, 'B%d' % r, "='Регулярность в плане'!O%d" % r, fmt='0.00'); put(wh, 'C%d' % r, "='Регулярность в плане'!P%d" % r, fmt='0.00')
    if i:
        put(wh, 'E%d' % (r + 1), '=A%d' % r, fmt='0.000'); put(wh, 'F%d' % (r + 1), round(W[L], 2), fmt='0.00')
        put(wh, 'H%d' % (r + 1), '=A%d' % r, fmt='0.000')
        put(wh, 'I%d' % (r + 1), round(X['F'][L], 2), fmt='0.00')
        put(wh, 'J%d' % (r + 1), round(Y['F'][L], 2), fmt='0.00')
hdr = ['отметка', 'высота этажа, м', 'Перемещение по Х, мм', 'Разность этажа по Х, мм', 'Регулярность по Х условие Ж1',
       'Перемещение по Y, мм', 'Разность этажа по Y, мм', 'Регулярность по Y условие Ж1']
for col, t in zip('ABCDEFGH', hdr): put(wh, col + '12', t, True, wrap=True)
for col, t in zip('KLMNOPQR', ['отметка', 'высота этажа, м', 'Масса j', 'Горизонтальная жесткость cj', 'Регулярность по Х условие Ж2',
                               'Масса j', 'Горизонтальная жесткость cj', 'Регулярность по Y условие Ж2']): put(wh, col + '12', t, True, wrap=True)
wh.row_dimensions[12].height = 60
for i in range(N):
    r = 13 + i; s = 2 + i
    put(wh, 'A%d' % r, '=A%d' % s, fmt='0.000'); put(wh, 'K%d' % r, '=A%d' % s, fmt='0.000')
    put(wh, 'C%d' % r, '=B%d' % s, fmt='0.00'); put(wh, 'F%d' % r, '=C%d' % s, fmt='0.00')
    if i < N - 1:
        put(wh, 'B%d' % r, '=A%d-A%d' % (r + 1, r), fmt='0.00'); put(wh, 'L%d' % r, '=K%d-K%d' % (r + 1, r), fmt='0.00')
        put(wh, 'D%d' % r, '=C%d-C%d' % (r + 1, r), fmt='0.00'); put(wh, 'G%d' % r, '=F%d-F%d' % (r + 1, r), fmt='0.00')
        put(wh, 'M%d' % r, '=F%d' % (s + 2), fmt='0.00'); put(wh, 'P%d' % r, '=M%d' % r, fmt='0.00')
        put(wh, 'N%d' % r, '=I%d/D%d' % (s + 2, r), fmt='0.00'); put(wh, 'Q%d' % r, '=J%d/G%d' % (s + 2, r), fmt='0.00')
last = 13 + N - 3
for r in range(13, last + 1):
    put(wh, 'E%d' % r, '=(D%d*B%d)/(D%d*B%d)' % (r, r + 1, r + 1, r), fmt='0.00'); put(wh, 'H%d' % r, '=(G%d*B%d)/(G%d*B%d)' % (r, r + 1, r + 1, r), fmt='0.00')
    put(wh, 'O%d' % r, '=((M%d*N%d)/(M%d*N%d))^0.5' % (r + 1, r, r, r + 1), fmt='0.00'); put(wh, 'R%d' % r, '=((P%d*Q%d)/(P%d*Q%d))^0.5' % (r + 1, r, r, r + 1), fmt='0.00')
for c in 'EHOR': put(wh, '%s19' % c, '=MAX(%s13:%s%d)' % (c, c, last), True, '0.00')
put(wh, 'E20', '=MAX(E19:R19)', True, '0.00')
for k, (t, f) in enumerate((('Регулярное по высоте ', '<=1.25'), ('Умеренно нерегулярное', '<=1.5'))):
    put(wh, 'A%d' % (21 + k), t); put(wh, 'E%d' % (21 + k), '=IF(E20%s,"OK","NO")' % f, True)
put(wh, 'A23', 'Чрезмерно нерегулярное '); put(wh, 'E23', '=IF(E20>1.5,"NO","OK")', True)
wh['A25'] = ('Массы и сейсмические силы — суммы по узлам уровня (CSV ЛИРА: «Распределение весов масс», «Инерционные силы», '
             'SRSS по значимым формам).'); wh['A25'].font = F()

# ---------------- Перекос этажа ----------------
wp = sheet('Перекос этажа')
put(wp, 'A1', 'Средние, мм', True); put(wp, 'B1', 'Х', True); put(wp, 'C1', 'У', True)
for i, L in enumerate(LV):
    r = 2 + i
    put(wp, 'A%d' % r, "='Регулярность в плане'!A%d" % r, fmt='0.000')
    put(wp, 'B%d' % r, round(X['disp_srss'][L]['avg'], 2), fmt='0.00'); put(wp, 'C%d' % r, round(Y['disp_srss'][L]['avg'], 2), fmt='0.00')
put(wp, 'F1', 'ε', True); put(wp, 'G1', 'q', True)
put(wp, 'F2', 0.02, fmt='0.000'); put(wp, 'G2', 3.9, fmt='0.00')
wp['H2'] = 'ε — табл. 7.11 СП РК 2.03-30-2017 (как в аналоге), q — коэффициент поведения модели'; wp['H2'].font = F()
wp['A6'] = 'Перемещения — SRSS по значимым формам (загр. 13: формы %s; загр. 14: формы %s), среднее по узлам перекрытия' % (
    d['modes']['13'], d['modes']['14']); wp['A6'].font = F()
for col, t in zip('ABCDEFGHIJ', ['отметка', 'высота этажа, м', 'Перемещение по Х, мм', 'Разность этажа по Х, мм',
                                 'Нормативный перекос этажа h·ε/q, мм', 'Проверка Х', 'Перемещение по Y, мм',
                                 'Разность этажа по Y, мм', 'Нормативный перекос этажа h·ε/q, мм', 'Проверка Y']):
    put(wp, col + '9', t, True, wrap=True)
wp.row_dimensions[9].height = 60
for i in range(N):
    r = 10 + i; s = 2 + i
    put(wp, 'A%d' % r, '=A%d' % s, fmt='0.000'); put(wp, 'C%d' % r, '=B%d' % s, fmt='0.00'); put(wp, 'G%d' % r, '=C%d' % s, fmt='0.00')
    if i < N - 1:
        put(wp, 'B%d' % r, '=A%d-A%d' % (r + 1, r), fmt='0.00')
        put(wp, 'D%d' % r, '=C%d-C%d' % (r + 1, r), fmt='0.00'); put(wp, 'H%d' % r, '=G%d-G%d' % (r + 1, r), fmt='0.00')
        put(wp, 'E%d' % r, '=((B%d*1000)*F$2)/G$2' % r, fmt='0.00'); put(wp, 'I%d' % r, '=((B%d*1000)*F$2)/G$2' % r, fmt='0.00')
        put(wp, 'F%d' % r, '=IF(E%d>D%d,"OK","NO")' % (r, r), True); put(wp, 'J%d' % r, '=IF(I%d>H%d,"OK","NO")' % (r, r), True)
wp.column_dimensions['A'].width = 16

# ---------------- Учет эффектов 2го рода ----------------
w2 = sheet('Учет эффектов 2го рода')
put(w2, 'D2', 'Средние', True); put(w2, 'E2', 'Х', True); put(w2, 'F2', 'У', True)
put(w2, 'H2', 'P tot, т', True); put(w2, 'I2', 'Х', True); put(w2, 'J2', 'У', True)
put(w2, 'L2', 'V tot, т', True); put(w2, 'M2', 'Х', True); put(w2, 'N2', 'У', True)
Ptot = {L: sum(W[LL] for LL in LV[i + 1:]) for i, L in enumerate(LV)}
Vt = {L: (X['V'][L], Y['V'][L]) for L in LV}
for i, L in enumerate(LV):
    r = 3 + i
    put(w2, 'D%d' % r, "='Перекос этажа'!A%d" % (2 + i), fmt='0.000')
    put(w2, 'E%d' % r, "='Перекос этажа'!B%d" % (2 + i), fmt='0.00'); put(w2, 'F%d' % r, "='Перекос этажа'!C%d" % (2 + i), fmt='0.00')
    put(w2, 'H%d' % r, '=D%d' % r, fmt='0.000'); put(w2, 'I%d' % r, round(Ptot[L], 2), fmt='0.00'); put(w2, 'J%d' % r, '=I%d' % r, fmt='0.00')
    put(w2, 'L%d' % r, '=D%d' % r, fmt='0.000'); put(w2, 'M%d' % r, round(Vt[L][0], 2), fmt='0.00'); put(w2, 'N%d' % r, round(Vt[L][1], 2), fmt='0.00')
put(w2, 'P2', 'q', True); put(w2, 'P3', "='Перекос этажа'!G2", fmt='0.00')
w2['P4'] = 'dr = q·(dk+1 - dk), п. 7.12.3 (7.31)'; w2['P4'].font = F()
put(w2, 'C14', 'Х', True); put(w2, 'O14', 'У', True)
for col, t in zip('ABCDEFGHIJ', ['Отметки', 'Высота этажа, м', 'Загружение', 'Перемещение К, мм', 'Перемещение К+1, мм',
                                 'dr = q·Δ, мм', 'Ptot, т', 'Vtot, т', 'Коэффициент θ', 'Проверка']):
    put(w2, col + '15', t, True, wrap=True)
for col, t in zip('MNOPQRSTUV', ['Отметки', 'Высота этажа, м', 'Загружение', 'Перемещение К, мм', 'Перемещение К+1, мм',
                                 'dr = q·Δ, мм', 'Ptot, т', 'Vtot, т', 'Коэффициент θ', 'Проверка']):
    put(w2, col + '15', t, True, wrap=True)
w2.row_dimensions[15].height = 45
for i in range(N):
    r = 16 + i; s = 3 + i
    put(w2, 'A%d' % r, '=D%d' % s, fmt='0.000'); put(w2, 'M%d' % r, '=A%d' % r, fmt='0.000')
    put(w2, 'C%d' % r, 'Сейсмическая по Х'); put(w2, 'O%d' % r, 'Сейсмическая по У')
    put(w2, 'D%d' % r, '=E%d' % s, fmt='0.00'); put(w2, 'P%d' % r, '=F%d' % s, fmt='0.00')
    if i < N - 1:
        put(w2, 'B%d' % r, '=A%d-A%d' % (r + 1, r), fmt='0.00'); put(w2, 'N%d' % r, '=M%d-M%d' % (r + 1, r), fmt='0.00')
        put(w2, 'E%d' % r, '=D%d' % (r + 1), fmt='0.00'); put(w2, 'Q%d' % r, '=P%d' % (r + 1), fmt='0.00')
        put(w2, 'F%d' % r, '=$P$3*(E%d-D%d)' % (r, r), fmt='0.00'); put(w2, 'R%d' % r, '=$P$3*(Q%d-P%d)' % (r, r), fmt='0.00')
        put(w2, 'G%d' % r, '=I%d' % s, fmt='0.00'); put(w2, 'S%d' % r, '=J%d' % s, fmt='0.00')
        put(w2, 'H%d' % r, '=M%d' % s, fmt='0.00'); put(w2, 'T%d' % r, '=N%d' % s, fmt='0.00')
        put(w2, 'I%d' % r, '=(G%d*F%d)/(H%d*B%d*1000)' % (r, r, r, r), fmt='0.000')
        put(w2, 'U%d' % r, '=(S%d*R%d)/(T%d*N%d*1000)' % (r, r, r, r), fmt='0.000')
        put(w2, 'J%d' % r, '=IF(I%d<=0.1,"OK",IF(I%d<=0.2,"1/(1-θ)","NO"))' % (r, r), True)
        put(w2, 'V%d' % r, '=IF(U%d<=0.1,"OK",IF(U%d<=0.2,"1/(1-θ)","NO"))' % (r, r), True)

# ---------------- Кручение (случайный эксцентриситет) ----------------
wt = sheet('Кручение')
put(wt, 'B1', 'Расчет крутящего момента по X', True); put(wt, 'P1', 'Расчет крутящего момента по Y', True)
H = ['Отметка', 'Fk, т', 'Lk, м', 'В, м', '1/4Lk, м', 'dkmax,мм', 'dkav,мм', 'ρ', 'fek', 'eak, м', 'Mak, тм', 'P=Mak/Lk/B/(1/4Lk), т/м2']
for j, t in enumerate(H):
    put(wt, '%s2' % 'BCDEFGHIJKLM'[j], t, True, wrap=True)
    put(wt, '%s2' % ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA'][j], t, True, wrap=True)
wt.row_dimensions[2].height = 45
for i in range(N - 1):
    r = 3 + i; s = 3 + i   # уровни выше -2.000
    put(wt, 'B%d' % r, "='Регулярность в плане'!A%d" % s, fmt='0.000')
    put(wt, 'C%d' % r, "='Регулярность по высоте'!I%d" % (r + 1), fmt='0.00')
    put(wt, 'D%d' % r, 12.0); put(wt, 'E%d' % r, 60.0); put(wt, 'F%d' % r, '=D%d/4' % r, fmt='0.00')
    put(wt, 'G%d' % r, "='Регулярность в плане'!B%d" % s, fmt='0.00'); put(wt, 'H%d' % r, "='Регулярность в плане'!O%d" % s, fmt='0.00')
    put(wt, 'I%d' % r, 1.2); put(wt, 'J%d' % r, '=I%d*((G%d/(1.1*H%d))^4)' % (r, r, r), fmt='0.000')
    put(wt, 'K%d' % r, '=0.05*D%d*J%d' % (r, r), fmt='0.000'); put(wt, 'L%d' % r, '=C%d*K%d' % (r, r), fmt='0.00')
    put(wt, 'M%d' % r, '=L%d/D%d/E%d/F%d' % (r, r, r, r), fmt='0.0000')
    put(wt, 'P%d' % r, '=B%d' % r, fmt='0.000'); put(wt, 'Q%d' % r, "='Регулярность по высоте'!J%d" % (r + 1), fmt='0.00')
    put(wt, 'R%d' % r, 60.0); put(wt, 'S%d' % r, 12.0); put(wt, 'T%d' % r, '=R%d/4' % r, fmt='0.00')
    put(wt, 'U%d' % r, "='Регулярность в плане'!D%d" % s, fmt='0.00'); put(wt, 'V%d' % r, "='Регулярность в плане'!P%d" % s, fmt='0.00')
    put(wt, 'W%d' % r, 1.2); put(wt, 'X%d' % r, '=W%d*((U%d/(1.1*V%d))^4)' % (r, r, r), fmt='0.000')
    put(wt, 'Y%d' % r, '=0.05*R%d*X%d' % (r, r), fmt='0.000'); put(wt, 'Z%d' % r, '=Q%d*Y%d' % (r, r), fmt='0.00')
    put(wt, 'AA%d' % r, '=Z%d/R%d/S%d/T%d' % (r, r, r, r), fmt='0.0000')
wt['B7'] = ('Lk — размер здания перпендикулярно направлению сейсмического воздействия (X: 12 м, Y: 60 м), '
            'eak = ±0,05·Lk·fek. Моменты случайного кручения в расчетную схему ЛИРА не введены.'); wt['B7'].font = F()

# ---------------- Опрокидывание ----------------
wo = sheet('Опрокидывание')
for col, t in zip('ABCDEFG', ['Направление', 'Вес здания G, т', 'Плечо B/2, м', 'Удерживающий момент, т·м',
                              'Опрокидывающий момент, т·м', 'Коэффициент устойчивости', 'Проверка ≥ 1,5']):
    put(wo, col + '1', t, True, wrap=True)
wo.row_dimensions[1].height = 45
Wtot = sum(W.values())
for r, (nm, B, M) in enumerate((('Сейсмика по X', 60.0, X['Mov']), ('Сейсмика по Y', 12.0, Y['Mov'])), 2):
    put(wo, 'A%d' % r, nm); put(wo, 'B%d' % r, round(Wtot, 2), fmt='0.00'); put(wo, 'C%d' % r, '=%g/2' % B, fmt='0.00')
    put(wo, 'D%d' % r, '=B%d*C%d' % (r, r), fmt='0.0'); put(wo, 'E%d' % r, round(M, 1), fmt='0.0')
    put(wo, 'F%d' % r, '=D%d/E%d' % (r, r), fmt='0.00'); put(wo, 'G%d' % r, '=IF(F%d>=1.5,"OK","NO")' % r, True)
wo['A5'] = ('G — сумма весов масс (CSV ЛИРА «Распределение весов масс»), опрокидывающий момент — SRSS по формам '
            'моментов инерционных сил относительно подошвы фундамента -2.000 (СП РК 2.03-30-2017 п. 8.4).'); wo['A5'].font = F()
for w in wb.worksheets:
    w.sheet_view.zoomScale = 85
wb.save(out)
print('ok', out, 'Wtot', round(Wtot, 1))
