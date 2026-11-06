# column break marks: clones of analog 6.6 breaks set by StartPoint/EndPoint (stretch points of SPDSBREAK are not independent)
def breaks(cols, X, ytop, ybot, tag):
    ops = []
    for i, (a, b) in enumerate(cols):
        for src, y, k in (('B6:42F9FB', ytop, 't'), ('B6:42F9FC', ybot, 'b')):
            tg = '%s_BR%d%s' % (tag, i, k)
            ops.append(dict(t='clone', h=src, base=[0, 0], to=[0, 0], tag=tg))
            ops.append(dict(t='mcset', h=tg, set={'StartPoint': [X(a), y], 'EndPoint': [X(b), y], 'ClipZonePoint': [X(b), y], 'Length': X(b) - X(a)}))
    return ops
