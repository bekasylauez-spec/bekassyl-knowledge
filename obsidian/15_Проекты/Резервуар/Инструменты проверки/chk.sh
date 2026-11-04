# full check: DXF + AutoCAD-exploded SPDS geometry -> oc.py (no silent skips)
cd /c/Users/Admin/AppData/Local/Temp/claude/D---------/22eb71ac-88c3-4c99-9c61-2c7547468f19/scratchpad/w
powershell -ExecutionPolicy Bypass -File ../net/job.ps1 -Ops ../ops/dx.json >/dev/null
powershell -ExecutionPolicy Bypass -File ../net/job.ps1 -Ops ../ops/gd.json >/dev/null
PYTHONIOENCODING=utf-8 python oc.py live.dxf sheets.json --geom=geom.txt > oc_out.txt 2>&1; grep -v " 0$" oc_out.txt
# PDFs of every sheet, then crops of every flagged spot
powershell -ExecutionPolicy Bypass -File ../net/job.ps1 -Ops ../ops/wb.json >/dev/null
powershell -ExecutionPolicy Bypass -File snap.ps1 -Scr "C:\Users\Admin\AppData\Local\Temp\claude\D---------\22eb71ac-88c3-4c99-9c61-2c7547468f19\scratchpad\pl\all.scr"
rm -f ../pl/look_*.png; PYTHONIOENCODING=utf-8 python look.py oc_out.txt
