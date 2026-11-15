from PIL import Image, ImageDraw, ImageFont
a = Image.open(r'D:\_claude_work\Kasymova\analog\c1_tl.png').convert('RGB')
b = Image.open(r'D:\_claude_work\Kasymova\revit\png\q_z4.png').convert('RGB')
H = 760
a = a.resize((int(a.width * H / a.height), H)); b = b.resize((int(b.width * H / b.height), H))
W = a.width + b.width + 30; im = Image.new('RGB', (W, H + 60), 'white'); im.paste(a, (0, 60)); im.paste(b, (a.width + 30, 60))
d = ImageDraw.Draw(im); f = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 30)
d.text((10, 12), 'Аналог: Онкоцентр 2.1 (ANSI36 x20)', fill='black', font=f)
d.text((a.width + 40, 12), 'Касымова 2.1 — жаңа штрих, колонна толық', fill='black', font=f)
d.line([(a.width + 15, 0), (a.width + 15, H + 60)], fill=(150, 150, 150), width=3)
im.save(r'C:\Users\Admin\AppData\Local\Temp\claude\825e6488202eeeff\94c03bfb-48e3-4972-8913-5871021722f0\scratchpad\Штрих_аналог_мен_жаңа.png'); print(im.size)
