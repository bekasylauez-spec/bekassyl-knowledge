import ezdxf, sys
doc = ezdxf.readfile(sys.argv[1])
for e in doc.modelspace().query('MTEXT'):
    if 'железобетонные, толщиной' in e.text or 'КОНСТРУКТИВНЫЕ' in e.text:
        print(e.dxf.handle, tuple(round(v) for v in e.dxf.insert)[:2], 'h', e.dxf.char_height, 'w', round(e.dxf.width))
        print(e.text)
        print('======')
