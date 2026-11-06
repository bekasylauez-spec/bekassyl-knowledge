# Re-set every formula of the template spec table in one op (AutoCAD drops neighbours when single cells are edited).
def spec_formulas(rows_pos=(1, 2, 3, 4, 5, 6, 7, 9, 14)):
    c = []
    for r in rows_pos:
        R = r + 1
        c += [[r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R)], [r, 12, 'L%d*K%d' % (R, R)]]
    c += [[10, 11, 'M15'], [10, 12, 'L11*K11'], [0, 12, 'Sum(M2:M11)']]
    return c
