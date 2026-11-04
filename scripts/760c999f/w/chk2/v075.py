import fitz,re,sys
sys.stdout.reconfigure(encoding='utf-8')
d=fitz.open(r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk2\pL2_sch\all.pdf')
print('sch still -0.100:',[i for i in range(d.page_count) if re.search(r'-0[.,]100',d[i].get_text())],'-0.750:',sum(len(re.findall(r'-0[.,]750',d[i].get_text())) for i in range(d.page_count)))
