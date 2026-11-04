import ezdxf, sys, re
doc = ezdxf.readfile(sys.argv[1])
msp = doc.modelspace()
for e in msp.query('ACAD_TABLE'):
    txt = []
    for tag in e.xtags if hasattr(e, 'xtags') else []:
        pass
    # raw: collect group code 1/2/3 strings from acdb table data
    raw = []
    try:
        for t in e.acdb_table.get_tags() if hasattr(e, 'acdb_table') else []:
            pass
    except Exception:
        pass
    s = ''
    try:
        from ezdxf.lldxf.tagwriter import TagCollector
        tc = TagCollector()
        e.export_dxf(tc)
        s = ' | '.join(str(t.value) for t in tc.tags if t.code in (1, 2, 3, 302, 303) and isinstance(t.value, str))
    except Exception as ex:
        s = 'ERR ' + str(ex)
    if 'Материал' in s or 'наброск' in s.lower() or 'бетона' in s:
        print(e.dxf.handle, tuple(round(v) for v in e.dxf.insert)[:2], s[:600])
        print('---')
