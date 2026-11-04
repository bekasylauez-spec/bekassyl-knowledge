import json, gen_marks as G
SP = (26325, -3225)
EX = {1: [('Фм-1', (2000, 29799, 5000, 29801))],
      2: [('Пм-1', (20174, 24500, 20176, 27500))],
      3: [('Пм-2', (20174, 24500, 20176, 27500))],
      4: [('Пм-3', (2500, 22874, 5500, 22876))],
      5: [('Пм-4', (3000, 9000, 3002, 9002)),
          ('Пм-5', (6675 + SP[0], 15224 + SP[1], 10275 + SP[0], 15226 + SP[1])),
          ('Пм-6', (10525 + SP[0], 18000 + SP[1], 10527 + SP[0], 21000 + SP[1])),
          ('ПтМ-2', (13175 + SP[0], 16500 + SP[1], 13375 + SP[0], 21500 + SP[1]))]}
for sh, E in EX.items():
    DX, DY = G.SH[sh]; X, Y = G.X21 + DX, G.Y21 + DY
    fx0 = -243621 + G.SW * (sh - 1); frame = (fx0, 455939, fx0 + G.SW, 497939)
    obst = G.load('w/live.dxf', 'w/geom.txt', frame)
    ops, miss = G.place(sh, X, Y, E, obst, X + 10025, Y + 11375, frame, 'MP%d_' % sh)
    print(sh, len(ops) // 3, miss)
    json.dump(ops, open('ops/mp%d.json' % sh, 'w', encoding='utf-8'), ensure_ascii=False)
