# sheet texts after a re-import: axis name, sheet numbers, notes (61d, sheet range), optional top title clone
import sys, json; sys.path.insert(0, 'wl'); from common import *
import ezdxf
def run(windows, repl, numbers, title=None):
    gx.run([{'t': 'dxfout', 'file': gx.S + r'\w\kt.dxf'}], 'dx')
    doc = ezdxf.readfile(gx.S + r'\w\kt.dxf'); msp = doc.modelspace(); ops = []
    for (X0, W, H) in windows:
        for e in msp.query('TEXT MTEXT'):
            p = e.dxf.insert
            if not (X0 < p.x < X0 + W and 455939 < p.y < 455939 + H): continue
            s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
            n = s
            for a, b in repl: n = n.replace(a, b)
            n = n.replace('^I', '\t')
            if s.strip() in numbers: n = numbers[s.strip()]
            if n != s: ops.append({'t': 'settext', 'h': e.dxf.handle, 's': n})
    if title: ops += title
    ops.append({'t': 'save'})
    print(len(ops), gx.run(ops, 'tx')[-30:])
if __name__ == '__main__':
    run([(889400, 59400, 42000)], [('по оси А стена', 'по оси А/1 стена'), ('КЖ-4.2 ... 4.4', 'КЖ-5.1 ... 5.4'), ('71d', '61d')], {'4.2': '5.2'},
        title=[{'t': 'clone', 'h': '140397', 'base': [948800, 0], 'to': [889400, 0], 'text': '{\LВертикальное армирование монолитной стены по оси А/1 стена См-1 (тол.250мм)}'}])
