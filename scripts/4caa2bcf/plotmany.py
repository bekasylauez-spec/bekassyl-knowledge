import plot, sys, gx, batch_util as bu
ks = [int(a) for a in sys.argv[1:]]
bu.restart(); plot.snap(); bu.kill()
for k in ks:
    SX = 172179 + 31500 * k
    pdf = plot.plot('p%d' % k, SX, 455939, SX + 31500, 470789, 'ISO без полей A1 (841.00 x 594.00 мм)')
    plot.png(pdf, gx.S + r'\w\p%d.png' % k, 85)
print('ok')
