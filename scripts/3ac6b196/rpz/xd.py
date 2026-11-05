import sys; sys.stdout.reconfigure(encoding="utf-8")
import openpyxl
for fn in sys.argv[1:]:
    wb = openpyxl.load_workbook(fn)
    print('=====', fn, wb.sheetnames)
    for ws in wb.worksheets:
        print('--- sheet', ws.title, ws.dimensions, 'imgs', len(ws._images), 'merged', len(ws.merged_cells.ranges))
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None: print('  ', c.coordinate, repr(c.value)[:120])
